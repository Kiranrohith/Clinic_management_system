from pydantic import BaseModel, Field

from app.models.enums import UserStatus
from app.schemas.validators import PhoneNumberStr


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
    phone: PhoneNumberStr | None = None
    qualification: str | None = Field(default=None, max_length=200)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    about: str | None = None
