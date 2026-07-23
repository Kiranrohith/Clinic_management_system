from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.events.sse import sse_manager
from app.models.communication import Notification
from app.models.enums import NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification import MarkAllReadResponse, NotificationResponse


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repository = NotificationRepository(db)
        self.user_repository = UserRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _to_response(item: Notification) -> NotificationResponse:
        return NotificationResponse(
            notification_id=item.notification_id,
            notification_type=item.notification_type.value if item.notification_type else None,
            title=item.title,
            message=item.message,
            is_read=item.is_read,
            created_at=item.created_at,
        )

    def create_for_user(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: dict | None = None,
    ) -> NotificationResponse:
        created = self.notification_repository.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            now=self._now(),
        )
        payload = {
            "notification_id": created.notification_id,
            "notification_type": notification_type.value,
            "title": created.title,
            "message": created.message,
            "created_at": created.created_at,
            "metadata": metadata or {},
        }
        sse_manager.publish(
            user_id=user_id,
            event_type=notification_type.value,
            payload=payload,
        )
        return self._to_response(created)

    def create_for_roles(
        self,
        role_names: tuple[str, ...],
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: dict | None = None,
    ) -> list[NotificationResponse]:
        responses: list[NotificationResponse] = []
        user_ids = self.user_repository.list_active_user_ids_by_roles(role_names)
        for user_id in user_ids:
            responses.append(
                self.create_for_user(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    metadata=metadata,
                )
            )
        return responses

    def list_for_user(self, user_id: int, unread_only: bool, limit: int) -> list[NotificationResponse]:
        rows = self.notification_repository.list_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )
        return [self._to_response(item) for item in rows]

    def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        return self.notification_repository.mark_as_read(user_id=user_id, notification_id=notification_id)

    def mark_all_as_read(self, user_id: int) -> MarkAllReadResponse:
        count = self.notification_repository.mark_all_as_read(user_id=user_id)
        return MarkAllReadResponse(updated_count=count)
