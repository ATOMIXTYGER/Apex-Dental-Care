from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Dentist
from app.schemas.user import UserCreate, UserUpdate, UserResponse, DentistProfileResponse
from app.schemas.common import MessageResponse
from app.security.dependencies import get_current_user, require_roles
from app.security.hashing import hash_password
from app.audit.service import log_audit_event

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("", response_model=List[UserResponse])
def get_users(
    role: Optional[str] = None,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """Admin-only: Retrieve all system users."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return [UserResponse.model_validate(u) for u in query.all()]

@router.get("/dentists", response_model=List[UserResponse])
def get_active_dentists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve list of all active dentists for appointment bookings and clinical operations."""
    dentists = db.query(User).filter(User.role == "dentist", User.is_active == True).all()
    return [UserResponse.model_validate(u) for u in dentists]

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """Admin-only: Create a new system user with optional dentist profile."""
    # Check duplicate email/username
    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "USER_EXISTS", "message": "A user with this email or username already exists."}
        )

    user = User(
        email=payload.email.lower(),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        phone=payload.phone,
        is_active=payload.is_active
    )
    db.add(user)
    db.flush()

    if payload.role == "dentist" and payload.dentist_profile:
        dentist = Dentist(
            user_id=user.id,
            license_number=payload.dentist_profile.license_number,
            specialization=payload.dentist_profile.specialization,
            qualifications=payload.dentist_profile.qualifications,
            cabin_number=payload.dentist_profile.cabin_number,
            is_active=payload.dentist_profile.is_active
        )
        db.add(dentist)

    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        action="USER_CREATE",
        user=current_user,
        entity_name="User",
        entity_id=str(user.id),
        details={"created_user": user.email, "role": user.role}
    )

    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """Admin-only: Update user details, role, or active status."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found."}
        )

    update_dict = payload.model_dump(exclude_unset=True)
    dentist_data = update_dict.pop("dentist_profile", None)
    pwd = update_dict.pop("password", None)
    if pwd:
        user.hashed_password = hash_password(pwd)

    for k, v in update_dict.items():
        setattr(user, k, v)

    if dentist_data and user.role == "dentist":
        if not user.dentist_profile:
            user.dentist_profile = Dentist(user_id=user.id, license_number=dentist_data.get("license_number", f"LIC-{user.id}"))
        for dk, dv in dentist_data.items():
            if dv is not None:
                setattr(user.dentist_profile, dk, dv)

    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        action="USER_UPDATE",
        user=current_user,
        entity_name="User",
        entity_id=str(user.id),
        details={"updated_fields": list(update_dict.keys())}
    )

    return UserResponse.model_validate(user)
