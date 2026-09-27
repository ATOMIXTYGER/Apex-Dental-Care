from typing import Optional, List
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.dental_chart import (
    ToothConditionUpdate, ToothConditionResponse, ToothHistoryResponse, DentalChartDetailResponse
)
from app.services.dental_service import DentalChartService
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/dental-chart", tags=["FDI Dental Chart"])

@router.get("/{patient_id}", response_model=DentalChartDetailResponse)
def get_patient_dental_chart(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full 32 permanent teeth chart, current conditions, and condition history."""
    return DentalChartService.get_full_chart_details(db, patient_id)

@router.post("/{patient_id}/tooth", response_model=ToothConditionResponse)
def update_tooth_condition(
    request: Request,
    patient_id: int,
    payload: ToothConditionUpdate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """
    Dentist-only: Update condition of an individual FDI permanent tooth (11-48).
    Creates an immutable history log preserving past states.
    """
    cond = DentalChartService.update_tooth_condition(
        db=db,
        patient_id=patient_id,
        data=payload,
        current_user=current_user,
        request=request
    )
    return ToothConditionResponse.model_validate(cond)

@router.get("/{patient_id}/tooth/{tooth_number}/history", response_model=List[ToothHistoryResponse])
def get_tooth_history(
    patient_id: int,
    tooth_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve complete clinical history for a single tooth."""
    records = DentalChartService.get_tooth_history(db, patient_id=patient_id, tooth_number=tooth_number)
    result = []
    for r in records:
        resp = ToothHistoryResponse.model_validate(r)
        resp.dentist_name = r.dentist.user.full_name if r.dentist and r.dentist.user else None
        result.append(resp)
    return result
