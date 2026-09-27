from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MedicineCatalogResponse(BaseModel):
    id: int
    name: str
    generic_name: Optional[str] = None
    dosage_form: str
    default_dosage: Optional[str] = None
    instructions: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PrescriptionItemCreate(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    timing: str = "After Food"
    instructions: Optional[str] = None

class PrescriptionItemResponse(PrescriptionItemCreate):
    id: int
    prescription_id: int
    model_config = ConfigDict(from_attributes=True)

class PrescriptionCreate(BaseModel):
    patient_id: int
    dentist_id: int
    visit_id: Optional[int] = None
    diagnosis_summary: Optional[str] = None
    general_instructions: Optional[str] = None
    items: List[PrescriptionItemCreate] = Field(min_length=1)

class PrescriptionResponse(BaseModel):
    id: int
    prescription_number: str
    patient_id: int
    dentist_id: int
    visit_id: Optional[int] = None
    diagnosis_summary: Optional[str] = None
    general_instructions: Optional[str] = None
    created_at: datetime
    dentist_name: Optional[str] = None
    patient_name: Optional[str] = None
    items: List[PrescriptionItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
