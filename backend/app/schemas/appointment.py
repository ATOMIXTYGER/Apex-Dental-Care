from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class AppointmentTypeResponse(BaseModel):
    id: int
    name: str
    duration_minutes: int
    color_code: str
    default_fee: int
    model_config = ConfigDict(from_attributes=True)

class AppointmentBase(BaseModel):
    patient_id: int
    dentist_id: int
    appointment_type_id: int | None = None
    appointment_date: date
    start_time: time
    end_time: time
    reason: str | None = None
    notes: str | None = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    dentist_id: int | None = None
    appointment_type_id: int | None = None
    appointment_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: str | None = None
    reason: str | None = None
    cancellation_reason: str | None = None
    notes: str | None = None

class AppointmentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(scheduled|confirmed|in_progress|completed|cancelled|no_show)$")
    cancellation_reason: str | None = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    cancellation_reason: str | None = None
    created_at: datetime
    patient_name: str | None = None
    patient_code: str | None = None
    dentist_name: str | None = None
    appointment_type_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
