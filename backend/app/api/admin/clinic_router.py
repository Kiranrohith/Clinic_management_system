from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin.clinic import ClinicSettingsUpsertRequest
from app.services.admin.clinic_service import AdminClinicService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/clinic-settings")
def get_clinic_settings(
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminClinicService(db).get_clinic_settings()
    if data is None:
        return success_response("Clinic settings not configured yet.", {})
    return success_response("Clinic settings fetched successfully.", data.model_dump())


@router.put("/clinic-settings")
def upsert_clinic_settings(
    payload: ClinicSettingsUpsertRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminClinicService(db).upsert_clinic_settings(payload, actor_user_id=current_user.user_id)
    return success_response("Clinic settings saved successfully.", data.model_dump())
