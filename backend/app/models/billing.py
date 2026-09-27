from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

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
    payment_method = Column(String(50), nullable=False) # cash, card, upi, bank_transfer, other
    transaction_reference = Column(String(100), nullable=True)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(Text, nullable=True)
    received_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
    patient = relationship("Patient")
    received_by = relationship("User")
