from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.communication import ContactQuery
from app.models.enums import ContactStatus


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_queries(self, status: ContactStatus | None, limit: int) -> list[ContactQuery]:
        stmt = select(ContactQuery)
        if status is not None:
            stmt = stmt.where(ContactQuery.status == status)
        stmt = stmt.order_by(ContactQuery.created_at.desc(), ContactQuery.contact_id.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_for_update(self, contact_id: int) -> ContactQuery | None:
        stmt = select(ContactQuery).where(ContactQuery.contact_id == contact_id).with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def save(self, contact_query: ContactQuery) -> ContactQuery:
        self.db.add(contact_query)
        self.db.flush()
        return contact_query
