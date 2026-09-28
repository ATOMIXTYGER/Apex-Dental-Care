from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProcedureCatalogResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    default_cost: Decimal
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)

class TreatmentItemCreate(BaseModel):
    procedure_name: str
    tooth_number: int | None = None
    estimated_cost: Decimal = Field(default=Decimal('0.00'), ge=0)
    notes: str | None = None

class TreatmentItemUpdate(BaseModel):
    procedure_name: str | None = None
    tooth_number: int | None = None
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    actual_cost: Decimal | None = Field(default=None, ge=0)
    status: str | None = None
    visit_id: int | None = None
    notes: str | None = None

class TreatmentItemResponse(BaseModel):
    id: int
    treatment_plan_id: int
    procedure_name: str
    tooth_number: int | None = None
    estimated_cost: Decimal
    actual_cost: Decimal
    status: str
    visit_id: int | None = None
    notes: str | None = None
    completed_at: datetime | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TreatmentPlanCreate(BaseModel):
    patient_id: int
    dentist_id: int
    title: str
    notes: str | None = None
    treatments: list[TreatmentItemCreate] = []

class TreatmentPlanUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    notes: str | None = None

class TreatmentPlanResponse(BaseModel):
    id: int
    patient_id: int
    dentist_id: int
    title: str
    status: str
    estimated_total: Decimal
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    dentist_name: str | None = None
    patient_name: str | None = None
    treatments: list[TreatmentItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
