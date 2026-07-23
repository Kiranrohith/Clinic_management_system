import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN, ROLE_FRONTDESK
from app.models.enums import NotificationType
from app.repositories.public.contact_repository import PublicContactRepository
from app.services.notification_service import NotificationService
from app.schemas.public.contact import (
    PublicContactQueryCreateRequest,
    PublicContactQueryResponse,
)

logger = logging.getLogger("clinic.public")


class PublicContactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PublicContactRepository(db)
        self.notification_service = NotificationService(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def create_contact_query(self, payload: PublicContactQueryCreateRequest) -> PublicContactQueryResponse:
        created = self.repo.create_contact_query(
            full_name=payload.full_name.strip(),
            phone=payload.phone.strip(),
            email=str(payload.email) if payload.email else None,
            subject=payload.subject.strip() if payload.subject else None,
            message=payload.message.strip(),
            now=self._now(),
        )
        logger.info("Contact query created contact_id=%s phone=%s", created.contact_id, created.phone)
        self.notification_service.create_for_roles(
            role_names=(ROLE_ADMIN, ROLE_FRONTDESK),
            notification_type=NotificationType.NEW_CONTACT_REQUEST,
            title="New contact request",
            message=f"New contact request received from {created.full_name}.",
            metadata={"contact_id": created.contact_id},
        )
        return PublicContactQueryResponse(
            contact_id=created.contact_id,
            full_name=created.full_name,
            phone=created.phone,
            email=created.email,
            subject=created.subject,
            message=created.message,
            status=created.status.value,
        )
