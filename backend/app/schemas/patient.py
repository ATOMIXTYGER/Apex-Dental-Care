from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime

class MedicalHistoryBase(BaseModel):
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    past_surgeries: Optional[str] = None
    bleeding_disorders: bool = False
    is_pregnant: bool = False
    notes: Optional[str] = None

class MedicalHistoryResponse(MedicalHistoryBase):
    id: int
    patient_id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DentalHistoryBase(BaseModel):
    chief_complaint: Optional[str] = None
    past_dental_treatments: Optional[str] = None
    brushing_frequency: Optional[str] = "Twice daily"
    flossing: bool = False
    habits: Optional[str] = None
    dental_anxiety_level: Optional[str] = "None"
    notes: Optional[str] = None

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
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_group: Optional[str] = None

class PatientCreate(PatientBase):
    medical_history: Optional[MedicalHistoryBase] = None
    dental_history: Optional[DentalHistoryBase] = None

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[MedicalHistoryBase] = None
    dental_history: Optional[DentalHistoryBase] = None

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
    medical_history: Optional[MedicalHistoryResponse] = None
    dental_history: Optional[DentalHistoryResponse] = None
    model_config = ConfigDict(from_attributes=True)
