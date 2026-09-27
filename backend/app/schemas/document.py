from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    visit_id: Optional[int] = None
    document_type: str
    file_name: str
    original_file_name: str
    file_size: int
    mime_type: str
    notes: Optional[str] = None
    uploaded_by_user_id: Optional[int] = None
    created_at: datetime
    patient_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    notes: Optional[str] = None
