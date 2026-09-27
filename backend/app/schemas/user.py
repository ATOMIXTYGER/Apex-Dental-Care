from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class DentistProfileBase(BaseModel):
    license_number: str
    specialization: str = "General Dentistry"
    qualifications: Optional[str] = None
    cabin_number: Optional[str] = None
    is_active: bool = True

class DentistProfileCreate(DentistProfileBase):
    pass

class DentistProfileResponse(DentistProfileBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=150)
    role: str = Field(default="receptionist") # admin, dentist, receptionist, patient
    phone: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    dentist_profile: Optional[DentistProfileCreate] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)
    dentist_profile: Optional[DentistProfileCreate] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    dentist_profile: Optional[DentistProfileResponse] = None
    model_config = ConfigDict(from_attributes=True)
