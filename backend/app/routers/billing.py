from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, status, Response, Request, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    PaymentOrderCreate,
    PaymentOrderResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
    PaymentRefundRequest,
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
    Receptionist/Admin: Record an offline manual payment against an invoice (cash, card swipe, manual UPI).
    Enforces balance checks and prevents overpayment or negative amounts.
    """
    payment = BillingService.record_payment(db, data=payload, current_user=current_user, request=request)
    return PaymentResponse.model_validate(payment)

# =========================================================================
# Online Payment Gateway Endpoints (Order, Verification, Webhooks, Receipts)
# =========================================================================

@router.post("/invoices/{invoice_id}/payments/order", response_model=PaymentOrderResponse, status_code=status.HTTP_201_CREATED)
def create_payment_order(
    invoice_id: int,
    request: Request,
    payload: Optional[PaymentOrderCreate] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an online payment order for checkout.
    Enforces server-side amount calculation, prevents overpayment, and creates a pending transaction.
    """
    data = payload or PaymentOrderCreate()
    return BillingService.create_payment_order(
        db=db,
        invoice_id=invoice_id,
        data=data,
        current_user=current_user,
        request=request
    )

@router.post("/payments/verify", response_model=PaymentVerifyResponse)
def verify_payment(
    request: Request,
    payload: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cryptographically verify payment success callback signature from checkout SDK.
    Executes an atomic transaction with row locking to update invoice balance and record audit log.
    """
    return BillingService.verify_payment(
        db=db,
        data=payload,
        current_user=current_user,
        request=request
    )

@router.post("/webhooks/{provider}")
async def handle_payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public asynchronous webhook listener for payment providers (e.g. Razorpay).
    Verifies raw HMAC-SHA256 signature and processes captured/failed events idempotently.
    """
    raw_body = await request.body()
    signature = (
        request.headers.get("X-Razorpay-Signature") or
        request.headers.get("x-razorpay-signature") or
        request.headers.get("X-Signature") or
        request.headers.get("x-signature") or
        ""
    )
    return BillingService.process_webhook(
        db=db,
        provider_name=provider,
        raw_body=raw_body,
        signature_header=signature,
        request=request
    )

@router.post("/payments/{payment_id}/reconcile", response_model=PaymentResponse)
def reconcile_payment(
    payment_id: int,
    request: Request,
    current_user: User = Depends(require_roles("admin", "receptionist")),
    db: Session = Depends(get_db)
):
    """
    Staff/Admin: Query payment gateway status and reconcile pending payment state.
    """
    payment = BillingService.reconcile_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user,
        request=request
    )
    return PaymentResponse.model_validate(payment)

@router.post("/payments/{payment_id}/refund", status_code=status.HTTP_200_OK)
def refund_payment(
    payment_id: int,
    request: Request,
    payload: PaymentRefundRequest,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """
    Admin: Issue full or partial refund on a successful settled payment.
    """
    refund = BillingService.refund_payment(
        db=db,
        payment_id=payment_id,
        data=payload,
        current_user=current_user,
        request=request
    )
    return {
        "status": "refunded",
        "refund_id": refund.id,
        "amount": refund.amount,
        "currency": refund.currency,
        "provider_refund_id": refund.provider_refund_id
    }

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve single payment transaction details."""
    payment = BillingService.get_payment_by_id(db, payment_id)
    return PaymentResponse.model_validate(payment)

@router.get("/payments/{payment_id}/receipt")
def download_payment_receipt(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and stream official payment receipt PDF."""
    pdf_bytes = BillingService.get_receipt_pdf(db, payment_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="receipt_{payment_id}.pdf"'
        }
    )

