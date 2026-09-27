from typing import Optional, List
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.billing import (
    InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentResponse
)
from app.services.billing_service import BillingService
from app.security.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])

@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve invoices with patient and status filtering."""
    invoices = BillingService.get_invoices(db, patient_id=patient_id, status_filter=status)
    result = []
    for inv in invoices:
        resp = InvoiceResponse.model_validate(inv)
        resp.patient_name = inv.patient.full_name if inv.patient else None
        result.append(resp)
    return result

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    request: Request,
    payload: InvoiceCreate,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """Receptionist/Admin: Create a new invoice with itemized procedures."""
    inv = BillingService.create_invoice(db, data=payload, current_user=current_user, request=request)
    resp = InvoiceResponse.model_validate(inv)
    resp.patient_name = inv.patient.full_name if inv.patient else None
    return resp

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve single invoice with item breakdown and payment history."""
    inv = BillingService.get_invoice_by_id(db, invoice_id)
    resp = InvoiceResponse.model_validate(inv)
    resp.patient_name = inv.patient.full_name if inv.patient else None
    return resp

@router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and stream clinic-branded invoice PDF."""
    pdf_bytes = BillingService.get_pdf(db, invoice_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="invoice_{invoice_id}.pdf"'
        }
    )

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    request: Request,
    payload: PaymentCreate,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """
    Receptionist/Admin: Record a payment against an invoice.
    Enforces balance checks and prevents overpayment or negative amounts.
    """
    payment = BillingService.record_payment(db, data=payload, current_user=current_user, request=request)
    return PaymentResponse.model_validate(payment)
