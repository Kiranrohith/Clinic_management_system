from pydantic import BaseModel, Field

from app.models.enums import UserStatus


class DoctorProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    phone: str | None
    role_name: str
    status: UserStatus
    qualification: str | None
    experience_years: int | None
    about: str | None
    specialization_names: list[str]


class DoctorProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=15)
    qualification: str | None = Field(default=None, max_length=200)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    about: str | None = None
