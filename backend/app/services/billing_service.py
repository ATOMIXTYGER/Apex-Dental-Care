from decimal import Decimal
from datetime import date, datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status, Request

from app.models.billing import Invoice, InvoiceItem, Payment
from app.models.patient import Patient
from app.models.user import User
from app.schemas.billing import InvoiceCreate, PaymentCreate
from app.pdf.generator import generate_invoice_pdf
from app.audit.service import log_audit_event

class BillingService:
    @staticmethod
    def _generate_invoice_number(db: Session) -> str:
        count = db.query(func.count(Invoice.id)).scalar() or 0
        return f"INV-2026-{1001 + count}"

    @classmethod
    def create_invoice(
        cls,
        db: Session,
        data: InvoiceCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Invoice:
        patient = db.query(Patient).filter(Patient.id == data.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": "Patient not found."}
            )

        invoice_num = cls._generate_invoice_number(db)
        
        # Calculate subtotal using exact Decimals
        subtotal = Decimal('0.00')
        for item in data.items:
            line_tot = Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
            subtotal += line_tot

        discount = Decimal(str(data.discount))
        tax = Decimal(str(data.tax))
        total = (subtotal - discount) + tax
        if total < Decimal('0.00'):
            total = Decimal('0.00')

        invoice = Invoice(
            invoice_number=invoice_num,
            patient_id=data.patient_id,
            visit_id=data.visit_id,
            treatment_plan_id=data.treatment_plan_id,
            issue_date=date.today(),
            due_date=data.due_date,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            paid_amount=Decimal('0.00'),
            balance=total,
            status="unpaid" if total > 0 else "paid",
            notes=data.notes
        )
        db.add(invoice)
        db.flush()

        for item in data.items:
            line_tot = Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                description=item.description,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total=line_tot
            )
            db.add(inv_item)

        db.commit()
        db.refresh(invoice)

        log_audit_event(
            db=db,
            action="INVOICE_CREATE",
            user=current_user,
            entity_name="Invoice",
            entity_id=str(invoice.id),
            details={"invoice_number": invoice.invoice_number, "total": str(invoice.total)},
            request=request
        )

        return invoice

    @classmethod
    def record_payment(
        cls,
        db: Session,
        data: PaymentCreate,
        current_user: User,
        request: Optional[Request] = None
    ) -> Payment:
        """
        Record a payment transaction with strict validation:
        - Prevents negative or zero payment
        - Prevents paying more than outstanding balance
        - Recalculates balance transactionally
        """
        # Lock or fetch invoice
        invoice = db.query(Invoice).filter(Invoice.id == data.invoice_id).with_for_update().first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "INVOICE_NOT_FOUND", "message": "Invoice not found."}
            )

        if invoice.status == "voided":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVOICE_VOIDED", "message": "Cannot record payments on a voided invoice."}
            )

        pay_amount = Decimal(str(data.amount))
        if pay_amount <= Decimal('0.00'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be greater than zero."}
            )

        if pay_amount > invoice.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "OVERPAYMENT_NOT_ALLOWED",
                    "message": f"Payment amount (${pay_amount:.2f}) exceeds current outstanding balance (${invoice.balance:.2f})."
                }
            )

        payment = Payment(
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            amount=pay_amount,
            payment_method=data.payment_method,
            transaction_reference=data.transaction_reference,
            payment_date=datetime.now(timezone.utc),
            notes=data.notes,
            received_by_user_id=current_user.id
        )
        db.add(payment)

        # Update invoice balance and status
        invoice.paid_amount += pay_amount
        invoice.balance = invoice.total - invoice.paid_amount
        if invoice.balance <= Decimal('0.00'):
            invoice.balance = Decimal('0.00')
            invoice.status = "paid"
        else:
            invoice.status = "partially_paid"

        db.commit()
        db.refresh(payment)
        db.refresh(invoice)

        log_audit_event(
            db=db,
            action="PAYMENT_CREATE",
            user=current_user,
            entity_name="Payment",
            entity_id=str(payment.id),
            details={"invoice_id": invoice.id, "amount": str(pay_amount), "balance": str(invoice.balance)},
            request=request
        )

        return payment

    @staticmethod
    def get_invoices(
        db: Session,
        patient_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Invoice]:
        query = db.query(Invoice)
        if patient_id:
            query = query.filter(Invoice.patient_id == patient_id)
        if status_filter:
            query = query.filter(Invoice.status == status_filter)
        return query.order_by(desc(Invoice.issue_date), desc(Invoice.id)).all()

    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "INVOICE_NOT_FOUND", "message": "Invoice not found."}
            )
        return invoice

    @classmethod
    def get_pdf(cls, db: Session, invoice_id: int) -> bytes:
        inv = cls.get_invoice_by_id(db, invoice_id)
        return generate_invoice_pdf(inv, inv.patient)
