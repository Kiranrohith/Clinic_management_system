from pydantic import BaseModel, EmailStr, Field

from app.schemas.validators import PhoneNumberStr


class AdminProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role_name: str


class AdminProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: PhoneNumberStr | None = None
