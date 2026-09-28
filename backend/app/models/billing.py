from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. INV-2026-001
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="SET NULL"), nullable=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id", ondelete="SET NULL"), nullable=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    subtotal = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    discount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    tax = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    total = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    balance = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    status = Column(String(50), default="unpaid", nullable=False, index=True) # unpaid, partially_paid, paid, voided
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    patient = relationship("Patient", back_populates="invoices")
    visit = relationship("Visit", back_populates="invoices")
    treatment_plan = relationship("TreatmentPlan")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    unit_price = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)

    invoice = relationship("Invoice", back_populates="items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    payment_method = Column(String(50), nullable=False) # cash, card, upi, bank_transfer, other
    transaction_reference = Column(String(100), nullable=True)
    payment_date = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    notes = Column(Text, nullable=True)
    received_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Online Payment Gateway Integration Fields
    status = Column(String(30), default="SUCCESS", nullable=False, index=True) # CREATED, PENDING, PROCESSING, SUCCESS, FAILED, REFUNDED
    provider = Column(String(50), default="manual", nullable=False, index=True) # manual, razorpay, mock
    provider_order_id = Column(String(100), nullable=True, index=True)
    provider_payment_id = Column(String(100), nullable=True, index=True)
    provider_signature = Column(String(255), nullable=True)
    idempotency_key = Column(String(100), unique=True, nullable=True, index=True)
    failure_reason = Column(Text, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
    patient = relationship("Patient")
    received_by = relationship("User")
    refunds = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")

class PaymentWebhookEvent(Base):
    __tablename__ = "payment_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    status = Column(String(30), default="processed", nullable=False) # processed, duplicate, failed
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    provider_refund_id = Column(String(100), nullable=True, index=True)
    reason = Column(Text, nullable=True)
    status = Column(String(30), default="SUCCESS", nullable=False) # SUCCESS, FAILED, PENDING
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    initiated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    payment = relationship("Payment", back_populates="refunds")
    initiated_by = relationship("User")
