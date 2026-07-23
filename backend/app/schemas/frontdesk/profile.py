from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserStatus


class FrontdeskProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role_name: str
    status: UserStatus


class FrontdeskProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, min_length=7, max_length=15)
