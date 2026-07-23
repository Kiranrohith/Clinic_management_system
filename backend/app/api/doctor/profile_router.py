from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.doctor.profile import DoctorProfileUpdateRequest
from app.services.doctor.profile_service import DoctorProfileService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


@router.get("/profile")
def get_profile(
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorProfileService(db).get_profile(current_user.user_id)
    return success_response("Doctor profile fetched successfully.", data.model_dump())


@router.put("/profile")
def update_profile(
    payload: DoctorProfileUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorProfileService(db).update_profile(current_user.user_id, payload)
    return success_response("Doctor profile updated successfully.", data.model_dump())
