from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.frontdesk.profile import FrontdeskProfileUpdateRequest
from app.services.frontdesk.profile_service import FrontdeskProfileService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.get("/profile")
def get_profile(
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskProfileService(db).get_profile(current_user)
    return success_response("Frontdesk profile fetched successfully.", data.model_dump())


@router.put("/profile")
def update_profile(
    payload: FrontdeskProfileUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskProfileService(db).update_profile(current_user.user_id, payload)
    return success_response("Frontdesk profile updated successfully.", data.model_dump())
