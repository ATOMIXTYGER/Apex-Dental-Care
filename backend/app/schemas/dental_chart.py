from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class ToothConditionUpdate(BaseModel):
    tooth_number: int
    condition: str = Field(pattern="^(healthy|caries|missing|filled|crown|root_canal|extraction|fracture|sensitivity|mobility|bridge|implant|impacted|other)$")
    severity: Optional[str] = "none" # none, mild, moderate, severe
    surfaces: Optional[str] = None # e.g. "O", "MO", "MOD", "B", "L"
    notes: Optional[str] = None
    visit_id: Optional[int] = None

    @field_validator("tooth_number")
    @classmethod
    def validate_fdi_number(cls, v):
        valid_quadrants = {1, 2, 3, 4}
        quadrant = v // 10
        tooth_pos = v % 10
        if quadrant not in valid_quadrants or tooth_pos < 1 or tooth_pos > 8:
            raise ValueError(f"Invalid FDI permanent tooth number: {v}. Must be in ranges 11-18, 21-28, 31-38, 41-48.")
        return v

class ToothConditionResponse(BaseModel):
    id: int
    patient_id: int
    tooth_number: int
    current_condition: str
    severity: Optional[str] = None
    surfaces: Optional[str] = None
    notes: Optional[str] = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ToothHistoryResponse(BaseModel):
    id: int
    patient_id: int
    visit_id: Optional[int] = None
    dentist_id: int
    dentist_name: Optional[str] = None
    tooth_number: int
    condition: str
    severity: Optional[str] = None
    surfaces: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DentalChartDetailResponse(BaseModel):
    patient_id: int
    teeth: Dict[int, ToothConditionResponse]
    history: List[ToothHistoryResponse]
