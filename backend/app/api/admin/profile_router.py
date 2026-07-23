from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin.profile import AdminProfileUpdateRequest
from app.services.admin.profile_service import AdminProfileService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/profile")
def get_admin_profile(
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminProfileService(db).get_admin_profile(current_user.user_id)
    return success_response("Admin profile fetched.", data.model_dump())


@router.put("/profile")
def update_admin_profile(
    payload: AdminProfileUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminProfileService(db).update_admin_profile(current_user.user_id, payload)
    return success_response("Admin profile updated.", data.model_dump())
