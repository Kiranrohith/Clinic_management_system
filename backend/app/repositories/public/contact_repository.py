from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.communication import ContactQuery
from app.models.enums import ContactStatus


class PublicContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_contact_query(
        self,
        full_name: str,
        phone: str,
        email: str | None,
        subject: str | None,
        message: str,
        now: datetime,
    ) -> ContactQuery:
        contact = ContactQuery(
            full_name=full_name,
            phone=phone,
            email=email,
            subject=subject,
            message=message,
            status=ContactStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        self.db.add(contact)
        self.db.flush()
        return contact
