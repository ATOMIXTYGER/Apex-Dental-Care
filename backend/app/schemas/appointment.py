from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime

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
    appointment_type_id: Optional[int] = None
    appointment_date: date
    start_time: time
    end_time: time
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    dentist_id: Optional[int] = None
    appointment_type_id: Optional[int] = None
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(scheduled|confirmed|in_progress|completed|cancelled|no_show)$")
    cancellation_reason: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    cancellation_reason: Optional[str] = None
    created_at: datetime
    patient_name: Optional[str] = None
    patient_code: Optional[str] = None
    dentist_name: Optional[str] = None
    appointment_type_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
