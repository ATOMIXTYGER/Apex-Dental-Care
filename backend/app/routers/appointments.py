from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.appointment import AppointmentType
from app.schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate, AppointmentResponse, AppointmentTypeResponse
)
from app.schemas.common import MessageResponse
from app.services.appointment_service import AppointmentService
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/appointments", tags=["Appointment Management"])

@router.get("/types", response_model=List[AppointmentTypeResponse])
def get_appointment_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve catalog of appointment types with colors and default durations."""
    types = db.query(AppointmentType).all()
    return [AppointmentTypeResponse.model_validate(t) for t in types]

@router.get("", response_model=List[AppointmentResponse])
def list_appointments(
    appointment_date: Optional[date] = None,
    dentist_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List appointments filtered by date, dentist, patient, or status."""
    appts = AppointmentService.get_appointments(
        db,
        appointment_date=appointment_date,
        dentist_id=dentist_id,
        patient_id=patient_id,
        status=status
    )
    result = []
    for a in appts:
        resp = AppointmentResponse.model_validate(a)
        resp.patient_name = a.patient.full_name if a.patient else None
        resp.patient_code = a.patient.patient_code if a.patient else None
        resp.dentist_name = a.dentist.user.full_name if a.dentist and a.dentist.user else None
        resp.appointment_type_name = a.appointment_type.name if a.appointment_type else None
        result.append(resp)
    return result

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    request: Request,
    payload: AppointmentCreate,
    current_user: User = Depends(require_roles("admin", "receptionist", "dentist")),
    db: Session = Depends(get_db)
):
    """Book an appointment with double-booking conflict prevention."""
    appt = AppointmentService.create_appointment(db, data=payload, current_user=current_user, request=request)
    resp = AppointmentResponse.model_validate(appt)
    resp.patient_name = appt.patient.full_name if appt.patient else None
    resp.patient_code = appt.patient.patient_code if appt.patient else None
    resp.dentist_name = appt.dentist.user.full_name if appt.dentist and appt.dentist.user else None
    resp.appointment_type_name = appt.appointment_type.name if appt.appointment_type else None
    return resp

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve appointment details."""
    appt = AppointmentService.get_appointment_by_id(db, appointment_id)
    resp = AppointmentResponse.model_validate(appt)
    resp.patient_name = appt.patient.full_name if appt.patient else None
    resp.patient_code = appt.patient.patient_code if appt.patient else None
    resp.dentist_name = appt.dentist.user.full_name if appt.dentist and appt.dentist.user else None
    resp.appointment_type_name = appt.appointment_type.name if appt.appointment_type else None
    return resp

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    request: Request,
    appointment_id: int,
    payload: AppointmentUpdate,
    current_user: User = Depends(require_roles("admin", "receptionist", "dentist")),
    db: Session = Depends(get_db)
):
    """Update or reschedule appointment."""
    appt = AppointmentService.update_appointment(db, appointment_id=appointment_id, data=payload, current_user=current_user, request=request)
    resp = AppointmentResponse.model_validate(appt)
    resp.patient_name = appt.patient.full_name if appt.patient else None
    resp.patient_code = appt.patient.patient_code if appt.patient else None
    resp.dentist_name = appt.dentist.user.full_name if appt.dentist and appt.dentist.user else None
    resp.appointment_type_name = appt.appointment_type.name if appt.appointment_type else None
    return resp

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    request: Request,
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    current_user: User = Depends(require_roles("admin", "receptionist", "dentist")),
    db: Session = Depends(get_db)
):
    """Change appointment status (confirmed, cancelled, no_show, completed)."""
    appt = AppointmentService.update_status(db, appointment_id=appointment_id, data=payload, current_user=current_user, request=request)
    resp = AppointmentResponse.model_validate(appt)
    resp.patient_name = appt.patient.full_name if appt.patient else None
    resp.patient_code = appt.patient.patient_code if appt.patient else None
    resp.dentist_name = appt.dentist.user.full_name if appt.dentist and appt.dentist.user else None
    resp.appointment_type_name = appt.appointment_type.name if appt.appointment_type else None
    return resp
