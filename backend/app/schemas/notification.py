from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    notification_id: int
    notification_type: str | None
    title: str | None
    message: str | None
    is_read: bool
    created_at: datetime | None


class MarkAllReadResponse(BaseModel):
    updated_count: int
