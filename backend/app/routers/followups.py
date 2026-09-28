
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.followup import FollowUpCreate, FollowUpResponse, FollowUpUpdate
from app.security.dependencies import get_current_user, require_roles
from app.services.followup_service import FollowUpService

router = APIRouter(prefix="/followups", tags=["Follow-Up Management"])

@router.get("", response_model=list[FollowUpResponse])
def list_followups(
    patient_id: int | None = None,
    dentist_id: int | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve scheduled follow-ups."""
    fus = FollowUpService.get_followups(db, patient_id=patient_id, dentist_id=dentist_id, status_filter=status)
    result = []
    for f in fus:
        resp = FollowUpResponse.model_validate(f)
        resp.patient_name = f.patient.full_name if f.patient else None
        resp.dentist_name = f.dentist.user.full_name if f.dentist and f.dentist.user else None
        result.append(resp)
    return result

@router.post("", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_followup(
    request: Request,
    payload: FollowUpCreate,
    current_user: User = Depends(require_roles("admin", "dentist", "receptionist")),
    db: Session = Depends(get_db)
):
    """Schedule a follow-up appointment or review date."""
    fu = FollowUpService.create_followup(db, data=payload, current_user=current_user, request=request)
    resp = FollowUpResponse.model_validate(fu)
    resp.patient_name = fu.patient.full_name if fu.patient else None
    resp.dentist_name = fu.dentist.user.full_name if fu.dentist and fu.dentist.user else None
    return resp

@router.put("/{followup_id}", response_model=FollowUpResponse)
def update_followup(
    request: Request,
    followup_id: int,
    payload: FollowUpUpdate,
    current_user: User = Depends(require_roles("admin", "dentist", "receptionist")),
    db: Session = Depends(get_db)
):
    """Update follow-up status (pending, completed, cancelled) or notes."""
    fu = FollowUpService.update_followup(db, followup_id=followup_id, data=payload, current_user=current_user, request=request)
    resp = FollowUpResponse.model_validate(fu)
    resp.patient_name = fu.patient.full_name if fu.patient else None
    resp.dentist_name = fu.dentist.user.full_name if fu.dentist and fu.dentist.user else None
    return resp
