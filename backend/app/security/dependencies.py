from datetime import datetime, UTC

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security.permissions import ROLE_PERMISSIONS, Permission, Role
from app.security.tokens import decode_access_token

security_scheme = HTTPBearer(auto_error=False)

def get_token_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme)
) -> str | None:
    """Retrieve access token from Bearer Authorization header or http-only cookie."""
    if credentials:
        return credentials.credentials
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    return None

def get_current_user(
    request: Request,
    token: str | None = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT access token and return active User object."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Authentication credentials were not provided"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Access token is invalid or has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN_PAYLOAD", "message": "Token does not contain user identification"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User associated with this token does not exist"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "This account is inactive. Contact the clinic administrator."},
        )

    if user.locked_until:
        locked = user.locked_until.replace(tzinfo=UTC) if user.locked_until.tzinfo is None else user.locked_until
        if locked > datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_LOCKED", "message": "Account temporarily locked due to failed login attempts."},
            )

    return user

def require_roles(*allowed_roles: str):
    """Enforce that current authenticated user belongs to one of allowed roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_ROLE",
                    "message": f"User role '{current_user.role}' is not authorized to access this resource. Allowed: {list(allowed_roles)}"
                }
            )
        return current_user
    return role_checker

def require_permission(permission: Permission):
    """Enforce granular permission check."""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = Role(current_user.role) if current_user.role in [r.value for r in Role] else None
        if not user_role or permission not in ROLE_PERMISSIONS.get(user_role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN_PERMISSION",
                    "message": f"Permission '{permission.value}' is required for this operation."
                }
            )
        return current_user
    return permission_checker
