from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class VisitBase(BaseModel):
    patient_id: int
    dentist_id: int
    appointment_id: int | None = None
    visit_date: date
    vitals_blood_pressure: str | None = None
    vitals_pulse: int | None = None
    chief_complaint: str | None = None
    oral_findings: str | None = None
    gum_condition: str | None = None
    hygiene_index: str | None = None
    diagnosis: str | None = None
    clinical_notes: str | None = None

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    vitals_blood_pressure: str | None = None
    vitals_pulse: int | None = None
    chief_complaint: str | None = None
    oral_findings: str | None = None
    gum_condition: str | None = None
    hygiene_index: str | None = None
    diagnosis: str | None = None
    clinical_notes: str | None = None

class VisitResponse(VisitBase):
    id: int
    created_at: datetime
    dentist_name: str | None = None
    patient_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
