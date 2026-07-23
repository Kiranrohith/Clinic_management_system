from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    safe_limit = max(1, min(limit, 200))
    data = NotificationService(db).list_for_user(
        user_id=current_user.user_id,
        unread_only=unread_only,
        limit=safe_limit,
    )
    return success_response("Notifications fetched successfully.", [item.model_dump() for item in data])


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updated = NotificationService(db).mark_as_read(
        user_id=current_user.user_id,
        notification_id=notification_id,
    )
    return success_response(
        "Notification marked as read.",
        {"updated": updated},
    )


@router.patch("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    data = NotificationService(db).mark_all_as_read(user_id=current_user.user_id)
    return success_response("Notifications marked as read.", data.model_dump())
