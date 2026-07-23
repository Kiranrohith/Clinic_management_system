from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.doctor.walkin import DoctorWalkInStatusUpdateRequest
from app.services.doctor.walkin_service import DoctorWalkInService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


@router.get("/walkin-tokens")
def list_walkin_tokens(
    token_date: date | None = None,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorWalkInService(db).list_walkin_tokens(current_user.user_id, token_date=token_date)
    return success_response("Doctor walk-in tokens fetched successfully.", [item.model_dump() for item in data])


@router.post("/walkin-tokens/{token_id}/status")
def update_walkin_status(
    token_id: int,
    payload: DoctorWalkInStatusUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorWalkInService(db).update_walkin_status(current_user.user_id, token_id, payload)
    return success_response("Walk-in token status updated successfully.", data.model_dump())
