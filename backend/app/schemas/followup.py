from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class FollowUpBase(BaseModel):
    patient_id: int
    dentist_id: int
    visit_id: Optional[int] = None
    scheduled_date: date
    reason: str
    notes: Optional[str] = None

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|completed|cancelled)$")
    notes: Optional[str] = None

class FollowUpResponse(FollowUpBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    patient_name: Optional[str] = None
    dentist_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
