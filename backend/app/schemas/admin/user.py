from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class DoctorProfileInput(BaseModel):
    qualification: str | None = Field(default=None, max_length=200)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    consultation_fee: float | None = Field(default=None, ge=0)
    about: str | None = None
    specialization_ids: list[int] = Field(default_factory=list)


class ManagementUserCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=15)
    role_name: Literal["ADMIN", "DOCTOR", "FRONTDESK"]
    doctor_profile: DoctorProfileInput | None = None


class ManagementUserResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role_name: str
    status: str
    created_at: str | None = None


class ManagementUserUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=15)


class UserStatusUpdateRequest(BaseModel):
    status: Literal["ACTIVE", "INACTIVE"]
