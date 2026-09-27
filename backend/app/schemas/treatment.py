from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProcedureCatalogResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    default_cost: Decimal
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TreatmentItemCreate(BaseModel):
    procedure_name: str
    tooth_number: Optional[int] = None
    estimated_cost: Decimal = Field(default=Decimal('0.00'), ge=0)
    notes: Optional[str] = None

class TreatmentItemUpdate(BaseModel):
    procedure_name: Optional[str] = None
    tooth_number: Optional[int] = None
    estimated_cost: Optional[Decimal] = Field(default=None, ge=0)
    actual_cost: Optional[Decimal] = Field(default=None, ge=0)
    status: Optional[str] = None
    visit_id: Optional[int] = None
    notes: Optional[str] = None

class TreatmentItemResponse(BaseModel):
    id: int
    treatment_plan_id: int
    procedure_name: str
    tooth_number: Optional[int] = None
    estimated_cost: Decimal
    actual_cost: Decimal
    status: str
    visit_id: Optional[int] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TreatmentPlanCreate(BaseModel):
    patient_id: int
    dentist_id: int
    title: str
    notes: Optional[str] = None
    treatments: List[TreatmentItemCreate] = []

class TreatmentPlanUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class TreatmentPlanResponse(BaseModel):
    id: int
    patient_id: int
    dentist_id: int
    title: str
    status: str
    estimated_total: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    dentist_name: Optional[str] = None
    patient_name: Optional[str] = None
    treatments: List[TreatmentItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
