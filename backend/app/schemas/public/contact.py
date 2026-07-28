from pydantic import BaseModel, EmailStr, Field

from app.schemas.validators import PhoneNumberStr


class PublicContactQueryCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: PhoneNumberStr
    email: EmailStr | None = None
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=1)


class PublicContactQueryResponse(BaseModel):
    contact_id: int
    full_name: str
    phone: str
    email: EmailStr | None
    subject: str | None
    message: str
    status: str
