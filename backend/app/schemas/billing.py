from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemCreate(BaseModel):
    description: str
    unit_price: Decimal = Field(ge=0)
    quantity: int = Field(default=1, ge=1)

class InvoiceItemResponse(BaseModel):
    id: int
    invoice_id: int
    description: str
    unit_price: Decimal
    quantity: int
    total: Decimal
    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    patient_id: int
    visit_id: int | None = None
    treatment_plan_id: int | None = None
    due_date: date
    discount: Decimal = Field(default=Decimal('0.00'), ge=0)
    tax: Decimal = Field(default=Decimal('0.00'), ge=0)
    notes: str | None = None
    items: list[InvoiceItemCreate] = Field(min_length=1)

class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=Decimal('0.00'))
    payment_method: str = Field(pattern="^(cash|card|upi|bank_transfer|other)$")
    transaction_reference: str | None = None
    notes: str | None = None

class PaymentOrderCreate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=Decimal('0.00'))
    idempotency_key: str | None = Field(default=None, max_length=100)

class PaymentOrderResponse(BaseModel):
    order_id: str
    internal_payment_id: int
    invoice_id: int
    amount: Decimal
    currency: str
    key_id: str
    provider: str
    clinic_name: str
    patient_name: str
    patient_email: str | None = None
    patient_phone: str | None = None
    is_test_mode: bool
    notes: dict = {}

class PaymentVerifyRequest(BaseModel):
    internal_payment_id: int
    provider_order_id: str
    provider_payment_id: str
    provider_signature: str
    invoice_id: int

class PaymentVerifyResponse(BaseModel):
    success: bool
    payment_id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: str
    transaction_reference: str
    balance_remaining: Decimal
    receipt_url: str

class PaymentRefundRequest(BaseModel):
    amount: Decimal | None = Field(default=None, gt=Decimal('0.00'))
    reason: str | None = None

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    patient_id: int
    amount: Decimal
    currency: str = "INR"
    payment_method: str
    status: str = "SUCCESS"
    provider: str = "manual"
    provider_order_id: str | None = None
    provider_payment_id: str | None = None
    transaction_reference: str | None = None
    payment_date: datetime
    notes: str | None = None
    received_by_user_id: int | None = None
    model_config = ConfigDict(from_attributes=True)

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    patient_id: int
    visit_id: int | None = None
    treatment_plan_id: int | None = None
    issue_date: date
    due_date: date
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    paid_amount: Decimal
    balance: Decimal
    status: str
    notes: str | None = None
    created_at: datetime
    patient_name: str | None = None
    items: list[InvoiceItemResponse] = []
    payments: list[PaymentResponse] = []
    model_config = ConfigDict(from_attributes=True)
