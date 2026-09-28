from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ToothConditionUpdate(BaseModel):
    tooth_number: int
    condition: str = Field(pattern="^(healthy|caries|missing|filled|crown|root_canal|extraction|fracture|sensitivity|mobility|bridge|implant|impacted|other)$")
    severity: str | None = "none" # none, mild, moderate, severe
    surfaces: str | None = None # e.g. "O", "MO", "MOD", "B", "L"
    notes: str | None = None
    visit_id: int | None = None

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
    severity: str | None = None
    surfaces: str | None = None
    notes: str | None = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ToothHistoryResponse(BaseModel):
    id: int
    patient_id: int
    visit_id: int | None = None
    dentist_id: int
    dentist_name: str | None = None
    tooth_number: int
    condition: str
    severity: str | None = None
    surfaces: str | None = None
    notes: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DentalChartDetailResponse(BaseModel):
    patient_id: int
    teeth: dict[int, ToothConditionResponse]
    history: list[ToothHistoryResponse]
