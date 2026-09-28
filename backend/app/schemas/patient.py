from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MedicalHistoryBase(BaseModel):
    allergies: str | None = None
    medical_conditions: str | None = None
    current_medications: str | None = None
    past_surgeries: str | None = None
    bleeding_disorders: bool = False
    is_pregnant: bool = False
    notes: str | None = None

class MedicalHistoryResponse(MedicalHistoryBase):
    id: int
    patient_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DentalHistoryBase(BaseModel):
    chief_complaint: str | None = None
    past_dental_treatments: str | None = None
    brushing_frequency: str | None = "Twice daily"
    flossing: bool = False
    habits: str | None = None
    dental_anxiety_level: str | None = "None"
    notes: str | None = None

class DentalHistoryResponse(DentalHistoryBase):
    id: int
    patient_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(pattern="^(Male|Female|Other)$")
    phone: str = Field(min_length=5, max_length=50)
    email: EmailStr | None = None
    address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    blood_group: str | None = None

class PatientCreate(PatientBase):
    medical_history: MedicalHistoryBase | None = None
    dental_history: DentalHistoryBase | None = None

class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    blood_group: str | None = None
    medical_history: MedicalHistoryBase | None = None
    dental_history: DentalHistoryBase | None = None

class PatientListItem(PatientBase):
    id: int
    patient_code: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PatientDetailResponse(PatientBase):
    id: int
    patient_code: str
    created_at: datetime
    updated_at: datetime
    medical_history: MedicalHistoryResponse | None = None
    dental_history: DentalHistoryResponse | None = None
    model_config = ConfigDict(from_attributes=True)
