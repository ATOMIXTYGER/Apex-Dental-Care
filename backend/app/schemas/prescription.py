from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MedicineCatalogResponse(BaseModel):
    id: int
    name: str
    generic_name: str | None = None
    dosage_form: str
    default_dosage: str | None = None
    instructions: str | None = None
    model_config = ConfigDict(from_attributes=True)

class PrescriptionItemCreate(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    timing: str = "After Food"
    instructions: str | None = None

class PrescriptionItemResponse(PrescriptionItemCreate):
    id: int
    prescription_id: int
    model_config = ConfigDict(from_attributes=True)

class PrescriptionCreate(BaseModel):
    patient_id: int
    dentist_id: int
    visit_id: int | None = None
    diagnosis_summary: str | None = None
    general_instructions: str | None = None
    items: list[PrescriptionItemCreate] = Field(min_length=1)

class PrescriptionResponse(BaseModel):
    id: int
    prescription_number: str
    patient_id: int
    dentist_id: int
    visit_id: int | None = None
    diagnosis_summary: str | None = None
    general_instructions: str | None = None
    created_at: datetime
    dentist_name: str | None = None
    patient_name: str | None = None
    items: list[PrescriptionItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
