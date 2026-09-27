from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

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
    visit_id: Optional[int] = None
    treatment_plan_id: Optional[int] = None
    due_date: date
    discount: Decimal = Field(default=Decimal('0.00'), ge=0)
    tax: Decimal = Field(default=Decimal('0.00'), ge=0)
    notes: Optional[str] = None
    items: List[InvoiceItemCreate] = Field(min_length=1)

class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=Decimal('0.00'))
    payment_method: str = Field(pattern="^(cash|card|upi|bank_transfer|other)$")
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    patient_id: int
    amount: Decimal
    payment_method: str
    transaction_reference: Optional[str] = None
    payment_date: datetime
    notes: Optional[str] = None
    received_by_user_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    patient_id: int
    visit_id: Optional[int] = None
    treatment_plan_id: Optional[int] = None
    issue_date: date
    due_date: date
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    paid_amount: Decimal
    balance: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    patient_name: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    payments: List[PaymentResponse] = []
    model_config = ConfigDict(from_attributes=True)
