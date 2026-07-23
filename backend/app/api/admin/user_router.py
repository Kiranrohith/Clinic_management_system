from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin.user import ManagementUserCreateRequest, ManagementUserUpdateRequest, UserStatusUpdateRequest
from app.services.admin.user_service import AdminUserService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/users")
def create_management_user(
    payload: ManagementUserCreateRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminUserService(db).create_management_user(payload, actor_user_id=current_user.user_id)
    return success_response("Management user created successfully.", data.model_dump())


@router.get("/users")
def list_management_users(
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminUserService(db).list_management_users()
    return success_response("Management users fetched successfully.", [item.model_dump() for item in data])


@router.put("/users/{user_id}/status")
def set_user_status(
    user_id: int,
    payload: UserStatusUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminUserService(db).set_user_status(user_id, payload, actor_user_id=current_user.user_id)
    return success_response("User status updated.", data.model_dump())


@router.put("/users/{user_id}")
def update_management_user(
    user_id: int,
    payload: ManagementUserUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminUserService(db).update_management_user(user_id, payload, actor_user_id=current_user.user_id)
    return success_response("User updated successfully.", data.model_dump())
