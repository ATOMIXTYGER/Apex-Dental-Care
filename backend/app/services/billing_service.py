import hashlib
import json
from datetime import date, datetime, UTC
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.audit.service import log_audit_event
from app.config import settings
from app.models.billing import (
    Invoice,
    InvoiceItem,
    Payment,
    PaymentRefund,
    PaymentWebhookEvent,
)
from app.models.patient import Patient
from app.models.user import User
from app.payments.factory import get_payment_provider
from app.pdf.generator import generate_invoice_pdf, generate_payment_receipt_pdf
from app.schemas.billing import (
    InvoiceCreate,
    PaymentCreate,
    PaymentOrderCreate,
    PaymentOrderResponse,
    PaymentRefundRequest,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)


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
        request: Request | None = None
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
        total = max(total, Decimal('0.00'))

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
        request: Request | None = None
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
                    "message": f"Payment amount (₹{pay_amount:.2f}) exceeds current outstanding balance (₹{invoice.balance:.2f})."
                }
            )

        payment = Payment(
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            amount=pay_amount,
            payment_method=data.payment_method,
            transaction_reference=data.transaction_reference,
            payment_date=datetime.now(UTC),
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
        patient_id: int | None = None,
        status_filter: str | None = None
    ) -> list[Invoice]:
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

    @classmethod
    def create_payment_order(
        cls,
        db: Session,
        invoice_id: int,
        data: PaymentOrderCreate,
        current_user: User,
        request: Request | None = None
    ) -> PaymentOrderResponse:
        """
        Create a secure payment gateway order for an invoice.
        Enforces server-side balance calculation, rejects overpayments, and supports idempotency.
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "INVOICE_NOT_FOUND", "message": "Invoice not found."}
            )

        if invoice.status == "voided":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVOICE_VOIDED", "message": "Cannot initiate payments on a voided invoice."}
            )

        if invoice.balance <= Decimal('0.00'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVOICE_ALREADY_PAID", "message": "This invoice is already paid in full."}
            )

        # Calculate exact amount to pay server-side
        amount_to_pay = Decimal(str(data.amount)) if data.amount is not None else invoice.balance
        if amount_to_pay <= Decimal('0.00'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be greater than zero."}
            )

        if amount_to_pay > invoice.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "OVERPAYMENT_NOT_ALLOWED",
                    "message": f"Payment amount (₹{amount_to_pay:.2f}) exceeds current outstanding balance (₹{invoice.balance:.2f})."
                }
            )

        # Idempotency check
        if data.idempotency_key:
            existing_payment = db.query(Payment).filter(Payment.idempotency_key == data.idempotency_key).first()
            if existing_payment:
                if existing_payment.status == "SUCCESS":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "IDEMPOTENT_PAYMENT_ALREADY_SUCCESS", "message": "A payment with this idempotency key was already completed."}
                    )
                elif existing_payment.status == "PENDING" and existing_payment.provider_order_id:
                    # Return existing pending order idempotently
                    provider = get_payment_provider(existing_payment.provider)
                    patient = invoice.patient
                    return PaymentOrderResponse(
                        order_id=existing_payment.provider_order_id,
                        internal_payment_id=existing_payment.id,
                        invoice_id=invoice.id,
                        amount=existing_payment.amount,
                        currency=existing_payment.currency,
                        key_id=provider.public_key_id,
                        provider=existing_payment.provider,
                        clinic_name=settings.CLINIC_NAME,
                        patient_name=patient.full_name if patient else "Valued Patient",
                        patient_email=patient.email if patient else None,
                        patient_phone=patient.phone if patient else None,
                        is_test_mode=(settings.PAYMENT_MODE == "test"),
                        notes={"invoice_number": invoice.invoice_number}
                    )

        # Obtain gateway provider
        provider = get_payment_provider()

        # Call provider abstraction to create order
        receipt_ref = f"inv_{invoice.id}_{date.today().strftime('%Y%m%d')}"
        notes_payload = {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "patient_id": str(invoice.patient_id)
        }

        order_res = provider.create_order(
            amount=amount_to_pay,
            currency=settings.PAYMENT_CURRENCY,
            receipt=receipt_ref,
            notes=notes_payload
        )

        # Persist pending internal payment record
        payment = Payment(
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            amount=amount_to_pay,
            currency=order_res.currency,
            payment_method="card", # default gateway method category (can be card/upi/netbanking)
            status="PENDING",
            provider=order_res.provider,
            provider_order_id=order_res.order_id,
            idempotency_key=data.idempotency_key,
            payment_date=datetime.now(UTC),
            received_by_user_id=current_user.id if current_user else None
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        log_audit_event(
            db=db,
            action="PAYMENT_ORDER_CREATED",
            user=current_user,
            entity_name="Payment",
            entity_id=str(payment.id),
            details={
                "invoice_id": invoice.id,
                "provider": order_res.provider,
                "order_id": order_res.order_id,
                "amount": str(amount_to_pay)
            },
            request=request
        )

        patient = invoice.patient
        return PaymentOrderResponse(
            order_id=order_res.order_id,
            internal_payment_id=payment.id,
            invoice_id=invoice.id,
            amount=amount_to_pay,
            currency=order_res.currency,
            key_id=provider.public_key_id,
            provider=order_res.provider,
            clinic_name=settings.CLINIC_NAME,
            patient_name=patient.full_name if patient else "Valued Patient",
            patient_email=patient.email if patient else None,
            patient_phone=patient.phone if patient else None,
            is_test_mode=(settings.PAYMENT_MODE == "test"),
            notes=notes_payload
        )

    @classmethod
    def verify_payment(
        cls,
        db: Session,
        data: PaymentVerifyRequest,
        current_user: User,
        request: Request | None = None
    ) -> PaymentVerifyResponse:
        """
        Cryptographically verifies payment signature server-side.
        Executes an atomic database transaction with row-level locks to update payment and invoice balance.
        """
        # Fetch payment record
        payment = db.query(Payment).filter(Payment.id == data.internal_payment_id).with_for_update().first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PAYMENT_NOT_FOUND", "message": "Payment record not found."}
            )

        # Idempotent response: If already verified, return success without re-crediting
        if payment.status == "SUCCESS":
            invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
            return PaymentVerifyResponse(
                success=True,
                payment_id=payment.id,
                invoice_id=payment.invoice_id,
                amount=payment.amount,
                currency=payment.currency,
                status="SUCCESS",
                transaction_reference=payment.transaction_reference or payment.provider_payment_id or "",
                balance_remaining=invoice.balance if invoice else Decimal('0.00'),
                receipt_url=f"/api/v1/billing/payments/{payment.id}/receipt"
            )

        # Verify IDOR / entity matching
        if payment.invoice_id != data.invoice_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVOICE_MISMATCH", "message": "Payment does not correspond to specified invoice."}
            )

        if payment.provider_order_id != data.provider_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ORDER_MISMATCH", "message": "Provider order ID mismatch."}
            )

        # Cryptographic signature verification
        provider = get_payment_provider(payment.provider)
        v_result = provider.verify_payment_signature(
            order_id=data.provider_order_id,
            payment_id=data.provider_payment_id,
            signature=data.provider_signature
        )

        if not v_result.is_valid:
            payment.status = "FAILED"
            payment.failure_reason = v_result.error_message or "Invalid signature"
            payment.provider_signature = data.provider_signature
            db.commit()

            log_audit_event(
                db=db,
                action="PAYMENT_VERIFICATION_FAILED",
                user=current_user,
                entity_name="Payment",
                entity_id=str(payment.id),
                details={"reason": payment.failure_reason, "provider_order_id": data.provider_order_id},
                request=request
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_SIGNATURE", "message": "Cryptographic payment verification failed."}
            )

        # Lock invoice record
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).with_for_update().first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "INVOICE_NOT_FOUND", "message": "Invoice not found."}
            )

        if invoice.status == "voided":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVOICE_VOIDED", "message": "Invoice has been voided."}
            )

        # Atomically transition payment and recalculate balance
        payment.status = "SUCCESS"
        payment.provider_payment_id = data.provider_payment_id
        payment.provider_signature = data.provider_signature
        payment.transaction_reference = data.provider_payment_id
        payment.paid_at = datetime.now(UTC)
        payment.payment_date = datetime.now(UTC)

        invoice.paid_amount += payment.amount
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
            action="PAYMENT_SUCCESS",
            user=current_user,
            entity_name="Payment",
            entity_id=str(payment.id),
            details={
                "invoice_id": invoice.id,
                "amount": str(payment.amount),
                "provider_payment_id": data.provider_payment_id,
                "balance": str(invoice.balance)
            },
            request=request
        )

        return PaymentVerifyResponse(
            success=True,
            payment_id=payment.id,
            invoice_id=invoice.id,
            amount=payment.amount,
            currency=payment.currency,
            status="SUCCESS",
            transaction_reference=data.provider_payment_id,
            balance_remaining=invoice.balance,
            receipt_url=f"/api/v1/billing/payments/{payment.id}/receipt"
        )

    @classmethod
    def process_webhook(
        cls,
        db: Session,
        provider_name: str,
        raw_body: bytes,
        signature_header: str,
        request: Request | None = None
    ) -> dict[str, Any]:
        """
        Process webhook notifications from the payment gateway.
        Validates raw HMAC-SHA256 signature and guarantees idempotent processing.
        """
        provider = get_payment_provider(provider_name)
        if not provider.verify_webhook_signature(raw_body, signature_header):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_WEBHOOK_SIGNATURE", "message": "Webhook signature verification failed."}
            )

        try:
            event_data = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_WEBHOOK_PAYLOAD", "message": "Malformed JSON payload."}
            ) from exc

        event_id = event_data.get("id") or event_data.get("event_id") or f"evt_{hashlib.md5(raw_body).hexdigest()}"
        event_type = event_data.get("event", "unknown")

        # Idempotency check for webhooks
        existing_event = db.query(PaymentWebhookEvent).filter(PaymentWebhookEvent.event_id == event_id).first()
        if existing_event:
            return {"status": "already_processed", "event_id": event_id}

        webhook_log = PaymentWebhookEvent(
            provider=provider_name,
            event_id=event_id,
            event_type=event_type,
            status="processed",
            payload=raw_body.decode("utf-8")
        )
        db.add(webhook_log)

        # Handle captured payment event
        if event_type in ("payment.captured", "order.paid"):
            payload_entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payload_entity.get("order_id") or event_data.get("payload", {}).get("order", {}).get("entity", {}).get("id")
            pay_id = payload_entity.get("id")

            if order_id:
                payment = db.query(Payment).filter(Payment.provider_order_id == order_id).with_for_update().first()
                if payment and payment.status != "SUCCESS":
                    invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).with_for_update().first()
                    payment.status = "SUCCESS"
                    if pay_id:
                        payment.provider_payment_id = pay_id
                        payment.transaction_reference = pay_id
                    payment.paid_at = datetime.now(UTC)

                    if invoice and invoice.status != "voided":
                        invoice.paid_amount += payment.amount
                        invoice.balance = invoice.total - invoice.paid_amount
                        if invoice.balance <= Decimal('0.00'):
                            invoice.balance = Decimal('0.00')
                            invoice.status = "paid"
                        else:
                            invoice.status = "partially_paid"

                    log_audit_event(
                        db=db,
                        action="PAYMENT_WEBHOOK_CAPTURED",
                        entity_name="Payment",
                        entity_id=str(payment.id),
                        details={"event_id": event_id, "provider_payment_id": pay_id},
                        request=request
                    )

        elif event_type == "payment.failed":
            payload_entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payload_entity.get("order_id")
            if order_id:
                payment = db.query(Payment).filter(Payment.provider_order_id == order_id).with_for_update().first()
                if payment and payment.status == "PENDING":
                    payment.status = "FAILED"
                    payment.failure_reason = payload_entity.get("error_description", "Payment failed at gateway")

        db.commit()
        return {"status": "success", "event_id": event_id}

    @classmethod
    def reconcile_payment(
        cls,
        db: Session,
        payment_id: int,
        current_user: User,
        request: Request | None = None
    ) -> Payment:
        """
        Reconcile a pending payment status directly with the payment gateway.
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).with_for_update().first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PAYMENT_NOT_FOUND", "message": "Payment record not found."}
            )

        if payment.status == "SUCCESS":
            return payment

        provider = get_payment_provider(payment.provider)
        lookup_id = payment.provider_payment_id or payment.provider_order_id
        if not lookup_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "NO_PROVIDER_REFERENCE", "message": "Payment has no provider order or transaction reference."}
            )

        details = provider.get_payment_details(lookup_id)
        if details.status == "captured":
            payment.status = "SUCCESS"
            if details.payment_id:
                payment.provider_payment_id = details.payment_id
                payment.transaction_reference = details.payment_id
            payment.paid_at = datetime.now(UTC)

            invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).with_for_update().first()
            if invoice and invoice.status != "voided":
                invoice.paid_amount += payment.amount
                invoice.balance = invoice.total - invoice.paid_amount
                if invoice.balance <= Decimal('0.00'):
                    invoice.balance = Decimal('0.00')
                    invoice.status = "paid"
                else:
                    invoice.status = "partially_paid"

            db.commit()
            db.refresh(payment)

            log_audit_event(
                db=db,
                action="PAYMENT_RECONCILED",
                user=current_user,
                entity_name="Payment",
                entity_id=str(payment.id),
                details={"status": "SUCCESS", "lookup_id": lookup_id},
                request=request
            )

        return payment

    @classmethod
    def refund_payment(
        cls,
        db: Session,
        payment_id: int,
        data: PaymentRefundRequest,
        current_user: User,
        request: Request | None = None
    ) -> PaymentRefund:
        """
        Admin: Issue full or partial refund for a successful payment.
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).with_for_update().first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PAYMENT_NOT_FOUND", "message": "Payment record not found."}
            )

        if payment.status != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "CANNOT_REFUND_NON_SUCCESS", "message": "Only successful payments can be refunded."}
            )

        refund_amount = Decimal(str(data.amount)) if data.amount is not None else payment.amount
        if refund_amount <= Decimal('0.00') or refund_amount > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_REFUND_AMOUNT", "message": f"Refund amount must be between ₹0.01 and ₹{payment.amount:.2f}."}
            )

        provider = get_payment_provider(payment.provider)
        lookup_id = payment.provider_payment_id or payment.transaction_reference or str(payment.id)
        rfnd_res = provider.refund_payment(
            provider_payment_id=lookup_id,
            amount=refund_amount,
            notes={"reason": data.reason or "Patient request"}
        )

        refund_entry = PaymentRefund(
            payment_id=payment.id,
            amount=refund_amount,
            currency=payment.currency,
            provider_refund_id=rfnd_res.refund_id,
            reason=data.reason,
            status="SUCCESS",
            initiated_by_user_id=current_user.id
        )
        db.add(refund_entry)

        # Adjust invoice balance
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).with_for_update().first()
        if invoice:
            invoice.paid_amount -= refund_amount
            invoice.balance = invoice.total - invoice.paid_amount
            if invoice.paid_amount <= Decimal('0.00'):
                invoice.status = "unpaid"
            else:
                invoice.status = "partially_paid"

        if refund_amount == payment.amount:
            payment.status = "REFUNDED"
        else:
            payment.status = "PARTIALLY_REFUNDED"

        db.commit()
        db.refresh(refund_entry)

        log_audit_event(
            db=db,
            action="PAYMENT_REFUNDED",
            user=current_user,
            entity_name="Payment",
            entity_id=str(payment.id),
            details={"refund_id": refund_entry.id, "amount": str(refund_amount), "reason": data.reason},
            request=request
        )

        return refund_entry

    @classmethod
    def get_payment_by_id(cls, db: Session, payment_id: int) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PAYMENT_NOT_FOUND", "message": "Payment record not found."}
            )
        return payment

    @classmethod
    def get_receipt_pdf(cls, db: Session, payment_id: int) -> bytes:
        payment = cls.get_payment_by_id(db, payment_id)
        if payment.status != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "RECEIPT_NOT_AVAILABLE", "message": "Receipts are only available for successfully settled payments."}
            )
        return generate_payment_receipt_pdf(payment, payment.invoice, payment.patient)

