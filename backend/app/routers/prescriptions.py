
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prescription import MedicineCatalog
from app.models.user import User
from app.schemas.prescription import (
    MedicineCatalogResponse,
    PrescriptionCreate,
    PrescriptionResponse,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["Prescription Management"])

@router.get("/catalog", response_model=list[MedicineCatalogResponse])
def get_medicine_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve catalog of standard clinic medications and default dosages."""
    medicines = db.query(MedicineCatalog).order_by(MedicineCatalog.name).all()
    return [MedicineCatalogResponse.model_validate(m) for m in medicines]

@router.get("", response_model=list[PrescriptionResponse])
def list_prescriptions(
    patient_id: int | None = None,
    dentist_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List prescriptions with optional patient or dentist filters."""
    rx_list = PrescriptionService.get_prescriptions(db, patient_id=patient_id, dentist_id=dentist_id)
    result = []
    for rx in rx_list:
        resp = PrescriptionResponse.model_validate(rx)
        resp.patient_name = rx.patient.full_name if rx.patient else None
        resp.dentist_name = rx.dentist.user.full_name if rx.dentist and rx.dentist.user else None
        result.append(resp)
    return result

@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(
    request: Request,
    payload: PrescriptionCreate,
    current_user: User = Depends(require_roles("dentist", "admin")),
    db: Session = Depends(get_db)
):
    """Dentist-only: Generate a digital prescription with medication schedule."""
    rx = PrescriptionService.create_prescription(db, data=payload, current_user=current_user, request=request)
    resp = PrescriptionResponse.model_validate(rx)
    resp.patient_name = rx.patient.full_name if rx.patient else None
    resp.dentist_name = rx.dentist.user.full_name if rx.dentist and rx.dentist.user else None
    return resp

@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve prescription details."""
    rx = PrescriptionService.get_prescription_by_id(db, prescription_id)
    resp = PrescriptionResponse.model_validate(rx)
    resp.patient_name = rx.patient.full_name if rx.patient else None
    resp.dentist_name = rx.dentist.user.full_name if rx.dentist and rx.dentist.user else None
    return resp

@router.get("/{prescription_id}/pdf")
def download_prescription_pdf(
    prescription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and securely stream clinic-branded prescription PDF."""
    pdf_bytes = PrescriptionService.get_pdf(db, prescription_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="prescription_{prescription_id}.pdf"'
        }
    )
