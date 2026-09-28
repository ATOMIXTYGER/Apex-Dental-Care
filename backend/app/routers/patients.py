from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.database import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.patient import (
    PatientCreate,
    PatientDetailResponse,
    PatientListItem,
    PatientUpdate,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patient Management"])

@router.get("", response_model=PaginatedResponse[PatientListItem])
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve paginated list of patients with search filtering."""
    items, total = PatientService.get_patients_paginated(db, page=page, page_size=page_size, search=search)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=[PatientListItem.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("", response_model=PatientDetailResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    request: Request,
    payload: PatientCreate,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """Register a new patient."""
    patient = PatientService.create_patient(db, data=payload, current_user=current_user, request=request)
    return PatientDetailResponse.model_validate(patient)

@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full patient demographic, medical, and dental history."""
    patient = PatientService.get_patient_by_id(db, patient_id)

    # Log patient view for compliance
    log_audit_event(
        db=db,
        action="PATIENT_VIEW",
        user=current_user,
        entity_name="Patient",
        entity_id=str(patient.id),
        details={"patient_code": patient.patient_code},
        request=request
    )

    return PatientDetailResponse.model_validate(patient)

@router.put("/{patient_id}", response_model=PatientDetailResponse)
def update_patient(
    request: Request,
    patient_id: int,
    payload: PatientUpdate,
    current_user: User = Depends(require_roles("admin", "receptionist", "dentist")),
    db: Session = Depends(get_db)
):
    """Update patient demographic or clinical history details."""
    patient = PatientService.update_patient(db, patient_id=patient_id, data=payload, current_user=current_user, request=request)
    return PatientDetailResponse.model_validate(patient)

@router.delete("/{patient_id}", response_model=MessageResponse)
def delete_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """Soft delete patient record."""
    PatientService.soft_delete_patient(db, patient_id=patient_id, current_user=current_user, request=request)
    return MessageResponse(message=f"Patient {patient_id} successfully archived.")

@router.get("/{patient_id}/timeline", response_model=list[dict[str, Any]])
def get_patient_timeline(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve complete chronological clinical history and event timeline."""
    return PatientService.get_patient_timeline(db, patient_id)
