from typing import List, Optional
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.clinical import VisitCreate, VisitUpdate, VisitResponse
from app.services.clinical_service import ClinicalService
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/visits", tags=["Clinical Examinations & Visits"])

@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(
    request: Request,
    payload: VisitCreate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Record a clinical examination and patient visit."""
    visit = ClinicalService.create_visit(db, data=payload, current_user=current_user, request=request)
    resp = VisitResponse.model_validate(visit)
    resp.patient_name = visit.patient.full_name if visit.patient else None
    resp.dentist_name = visit.dentist.user.full_name if visit.dentist and visit.dentist.user else None
    return resp

@router.get("/{visit_id}", response_model=VisitResponse)
def get_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve visit details and examination findings."""
    visit = ClinicalService.get_visit_by_id(db, visit_id)
    resp = VisitResponse.model_validate(visit)
    resp.patient_name = visit.patient.full_name if visit.patient else None
    resp.dentist_name = visit.dentist.user.full_name if visit.dentist and visit.dentist.user else None
    return resp

@router.get("/patient/{patient_id}", response_model=List[VisitResponse])
def get_patient_visits(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all historical visits for a patient."""
    visits = ClinicalService.get_patient_visits(db, patient_id)
    result = []
    for v in visits:
        resp = VisitResponse.model_validate(v)
        resp.patient_name = v.patient.full_name if v.patient else None
        resp.dentist_name = v.dentist.user.full_name if v.dentist and v.dentist.user else None
        result.append(resp)
    return result

@router.put("/{visit_id}", response_model=VisitResponse)
def update_visit(
    request: Request,
    visit_id: int,
    payload: VisitUpdate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Update examination notes or vitals."""
    visit = ClinicalService.update_visit(db, visit_id=visit_id, data=payload, current_user=current_user, request=request)
    resp = VisitResponse.model_validate(visit)
    resp.patient_name = visit.patient.full_name if visit.patient else None
    resp.dentist_name = visit.dentist.user.full_name if visit.dentist and visit.dentist.user else None
    return resp
