from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    visit_id: int | None = None
    document_type: str
    file_name: str
    original_file_name: str
    file_size: int
    mime_type: str
    notes: str | None = None
    uploaded_by_user_id: int | None = None
    created_at: datetime
    patient_name: str | None = None
    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    document_type: str | None = None
    notes: str | None = None
