from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FollowUpBase(BaseModel):
    patient_id: int
    dentist_id: int
    visit_id: int | None = None
    scheduled_date: date
    reason: str
    notes: str | None = None

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(BaseModel):
    scheduled_date: date | None = None
    reason: str | None = None
    status: str | None = Field(default=None, pattern="^(pending|completed|cancelled)$")
    notes: str | None = None

class FollowUpResponse(FollowUpBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    patient_name: str | None = None
    dentist_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
