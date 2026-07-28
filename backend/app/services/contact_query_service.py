from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN, ROLE_DOCTOR, ROLE_FRONTDESK
from app.models.enums import ContactStatus, NotificationType
from app.repositories.contact_repository import ContactRepository
from app.repositories.user_repository import UserRepository
from app.schemas.contact import ContactQueryItemResponse, ContactQueryUpdateRequest
from app.services.notification_service import NotificationService

MANAGEMENT_ROLES = (ROLE_ADMIN, ROLE_FRONTDESK, ROLE_DOCTOR)


class ContactQueryService:
    def __init__(self, db: Session):
        self.db = db
        self.contact_repository = ContactRepository(db)
        self.user_repository = UserRepository(db)
        self.notification_service = NotificationService(db)

    def list_queries(
        self,
        actor_user_id: int,
        actor_role: str,
        status_filter: ContactStatus | None,
        limit: int,
    ) -> list[ContactQueryItemResponse]:
        if limit < 1 or limit > 200:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="limit must be between 1 and 200")

        items = self.contact_repository.list_queries(status_filter, limit)
        return [self._to_response(item) for item in items]

    def update_query(
        self,
        actor_user_id: int,
        actor_role: str,
        contact_id: int,
        payload: ContactQueryUpdateRequest,
    ) -> ContactQueryItemResponse:
        handled_by = payload.handled_by_user_id if payload.handled_by_user_id is not None else actor_user_id
        assignee = self.user_repository.get_by_id(handled_by)
        if assignee is None or assignee.role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
        if assignee.role.role_name not in MANAGEMENT_ROLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user must be a management user")

        contact = self.contact_repository.get_for_update(contact_id)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact query not found")

        contact.status = payload.status
        contact.handled_by = handled_by
        contact.notes = payload.notes
        self.contact_repository.save(contact)
        self.db.commit()
        self.db.refresh(contact)

        receiver_ids = self.user_repository.list_active_user_ids_by_roles((ROLE_ADMIN, ROLE_FRONTDESK))
        unique_ids = sorted(set(receiver_ids))
        for user_id in unique_ids:
            self.notification_service.create_for_user(
                user_id=user_id,
                notification_type=NotificationType.NEW_CONTACT_REQUEST,
                title="Contact query updated",
                message=f"Contact query #{contact.contact_id} moved to {contact.status.value}.",
                metadata={
                    "contact_id": contact.contact_id,
                    "status": contact.status.value,
                    "handled_by": contact.handled_by,
                },
            )

        return self._to_response(contact)

    @staticmethod
    def _to_response(contact_query) -> ContactQueryItemResponse:
        return ContactQueryItemResponse(
            contact_id=contact_query.contact_id,
            full_name=contact_query.full_name,
            phone=contact_query.phone,
            email=contact_query.email,
            subject=contact_query.subject,
            message=contact_query.message,
            status=contact_query.status,
            handled_by=contact_query.handled_by,
            notes=contact_query.notes,
            created_at=contact_query.created_at,
            updated_at=contact_query.updated_at,
        )
