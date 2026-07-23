from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.communication import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        notification_type,
        title: str,
        message: str,
        now: datetime,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            is_read=False,
            created_at=now,
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_for_user(self, user_id: int, unread_only: bool, limit: int) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc(), Notification.notification_id.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.notification_id == notification_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        result = self.db.execute(stmt)
        return bool(result.rowcount and result.rowcount > 0)

    def mark_all_as_read(self, user_id: int) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        result = self.db.execute(stmt)
        return int(result.rowcount or 0)
