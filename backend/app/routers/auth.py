
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserResponse
from app.security.dependencies import get_current_user
from app.security.hashing import hash_password, verify_password
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: Request, response: Response, payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username/email and password."""
    user, access_token, refresh_token = AuthService.authenticate_user(
        db=db,
        username_or_email=payload.username_or_email,
        password=payload.password,
        request=request
    )

    # Set secure HTTP-only cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in production with HTTPS
        max_age=7 * 24 * 3600
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=60 * 60,
        user=UserResponse.model_validate(user)
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, payload: RefreshTokenRequest | None = None, db: Session = Depends(get_db)):
    """Refresh expired access token using refresh token from body or cookie."""
    token = (payload.refresh_token if payload else None) or request.cookies.get("refresh_token")
    if not token:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_REFRESH_TOKEN", "message": "No refresh token provided."}
        )

    user, access_token, new_refresh = AuthService.refresh_access_token(db=db, raw_refresh_token=token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 3600
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh,
        expires_in=60 * 60,
        user=UserResponse.model_validate(user)
    )

@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    payload: RefreshTokenRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke refresh session and clear cookie."""
    token = (payload.refresh_token if payload else None) or request.cookies.get("refresh_token")
    if token:
        AuthService.revoke_refresh_token(db=db, raw_refresh_token=token, user=current_user, request=request)

    response.delete_cookie(key="refresh_token")
    return MessageResponse(message="Successfully logged out.")

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile of currently authenticated user."""
    return UserResponse.model_validate(current_user)

@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INCORRECT_PASSWORD", "message": "Current password does not match."}
        )

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()

    log_audit_event(
        db=db,
        action="PASSWORD_CHANGE",
        user=current_user,
        entity_name="User",
        entity_id=str(current_user.id),
        details="User changed password"
    )

    return MessageResponse(message="Password successfully updated.")
