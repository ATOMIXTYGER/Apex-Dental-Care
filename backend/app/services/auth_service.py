from datetime import datetime, timedelta, UTC

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.config import settings
from app.models.user import RefreshToken, User
from app.security.hashing import verify_password
from app.security.tokens import create_access_token, generate_refresh_token, hash_token


class AuthService:
    @staticmethod
    def authenticate_user(
        db: Session,
        username_or_email: str,
        password: str,
        request: Request | None = None
    ) -> tuple[User, str, str]:
        """Authenticate user with rate-limiting / lock protection."""
        user = db.query(User).filter(
            (User.email == username_or_email.lower()) | (User.username == username_or_email)
        ).first()

        if not user:
            # Audit failed attempt
            log_audit_event(
                db=db,
                action="LOGIN_FAILURE",
                user_email=username_or_email,
                entity_name="User",
                details={"reason": "User not found"},
                request=request
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect username/email or password."}
            )

        # Check locked status
        now = datetime.now(UTC)
        if user.locked_until:
            locked = user.locked_until.replace(tzinfo=UTC) if user.locked_until.tzinfo is None else user.locked_until
            if locked > now:
                log_audit_event(
                    db=db,
                    action="LOGIN_LOCKED",
                    user=user,
                    entity_name="User",
                    entity_id=str(user.id),
                    details={"locked_until": str(user.locked_until)},
                    request=request
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "ACCOUNT_LOCKED", "message": "Account is temporarily locked. Try again later."}
                )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "Account is inactive. Contact the clinic administrator."}
            )

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
                details = "Account locked for 15 minutes due to 5 consecutive failures."
            else:
                details = f"Failed attempts: {user.failed_login_attempts}"

            db.commit()
            log_audit_event(
                db=db,
                action="LOGIN_FAILURE",
                user=user,
                entity_name="User",
                entity_id=str(user.id),
                details={"reason": "Password mismatch", "attempts": user.failed_login_attempts, "info": details},
                request=request
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect username/email or password."}
            )

        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

        # Generate tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "email": user.email, "name": user.full_name}
        )
        raw_refresh_token = generate_refresh_token()
        refresh_hash = hash_token(raw_refresh_token)

        # Store refresh token record
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_record)
        db.commit()

        # Audit successful login
        log_audit_event(
            db=db,
            action="LOGIN",
            user=user,
            entity_name="User",
            entity_id=str(user.id),
            details="User logged in successfully",
            request=request
        )

        return user, access_token, raw_refresh_token

    @staticmethod
    def refresh_access_token(db: Session, raw_refresh_token: str) -> tuple[User, str, str]:
        """Validate refresh token and issue new token pair (Token Rotation)."""
        now = datetime.now(UTC)
        refresh_hash = hash_token(raw_refresh_token)

        token_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == refresh_hash,
            RefreshToken.revoked == False
        ).first()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_REFRESH_TOKEN", "message": "Refresh token is invalid or expired."}
            )

        exp = token_record.expires_at.replace(tzinfo=UTC) if token_record.expires_at.tzinfo is None else token_record.expires_at
        if exp < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_REFRESH_TOKEN", "message": "Refresh token is invalid or expired."}
            )

        # Revoke used refresh token for rotation
        token_record.revoked = True

        user = db.query(User).filter(User.id == token_record.user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "USER_NOT_FOUND", "message": "User not found or inactive."}
            )

        # Generate new pair
        new_access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "email": user.email, "name": user.full_name}
        )
        new_raw_refresh = generate_refresh_token()
        new_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_raw_refresh),
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_record)
        db.commit()

        return user, new_access_token, new_raw_refresh

    @staticmethod
    def revoke_refresh_token(db: Session, raw_refresh_token: str, user: User | None = None, request: Request | None = None):
        """Revoke a refresh token on logout."""
        refresh_hash = hash_token(raw_refresh_token)
        token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == refresh_hash).first()
        if token_record:
            token_record.revoked = True
            db.commit()

        if user:
            log_audit_event(
                db=db,
                action="LOGOUT",
                user=user,
                entity_name="User",
                entity_id=str(user.id),
                details="User logged out successfully",
                request=request
            )
