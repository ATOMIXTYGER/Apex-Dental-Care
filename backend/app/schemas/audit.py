from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    user_email: str | None = None
    action: str
    entity_name: str | None = None
    entity_id: str | None = None
    details: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
