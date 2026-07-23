from pydantic import BaseModel, EmailStr, Field


class AdminProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role_name: str


class AdminProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=15)
