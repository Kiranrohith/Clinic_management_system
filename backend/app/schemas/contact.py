from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ContactStatus


class ContactQueryItemResponse(BaseModel):
    contact_id: int
    full_name: str
    phone: str
    email: str | None
    subject: str | None
    message: str
    status: ContactStatus
    handled_by: int | None
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None


class ContactQueryUpdateRequest(BaseModel):
    status: ContactStatus
    notes: str | None = None
    handled_by_user_id: int | None = Field(default=None, ge=1)
