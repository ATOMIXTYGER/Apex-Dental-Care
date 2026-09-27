from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime

class VisitBase(BaseModel):
    patient_id: int
    dentist_id: int
    appointment_id: Optional[int] = None
    visit_date: date
    vitals_blood_pressure: Optional[str] = None
    vitals_pulse: Optional[int] = None
    chief_complaint: Optional[str] = None
    oral_findings: Optional[str] = None
    gum_condition: Optional[str] = None
    hygiene_index: Optional[str] = None
    diagnosis: Optional[str] = None
    clinical_notes: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    vitals_blood_pressure: Optional[str] = None
    vitals_pulse: Optional[int] = None
    chief_complaint: Optional[str] = None
    oral_findings: Optional[str] = None
    gum_condition: Optional[str] = None
    hygiene_index: Optional[str] = None
    diagnosis: Optional[str] = None
    clinical_notes: Optional[str] = None

class VisitResponse(VisitBase):
    id: int
    created_at: datetime
    dentist_name: Optional[str] = None
    patient_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
