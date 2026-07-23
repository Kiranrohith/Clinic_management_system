from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.frontdesk.walkin import (
    FrontdeskWalkInCreateRequest,
    FrontdeskWalkInStatusUpdateRequest,
)
from app.services.frontdesk.walkin_service import FrontdeskWalkInService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.post("/walkin-tokens")
def create_walkin_token(
    payload: FrontdeskWalkInCreateRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskWalkInService(db).create_walkin_token(payload, actor_user_id=current_user.user_id)
    return success_response("Walk-in token created successfully.", data.model_dump())


@router.get("/walkin-tokens/today")
def list_today_walkin_tokens(
    doctor_user_id: int | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskWalkInService(db).list_walkin_token_history(token_date=date.today(), doctor_user_id=doctor_user_id)
    return success_response("Today's walk-in tokens fetched successfully.", [item.model_dump() for item in data])


@router.get("/walkin-tokens")
def list_walkin_tokens(
    doctor_user_id: int | None = None,
    token_date: date | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskWalkInService(db).list_walkin_token_history(token_date=token_date, doctor_user_id=doctor_user_id)
    return success_response("Walk-in tokens fetched successfully.", [item.model_dump() for item in data])


@router.get("/walkin-tokens/{token_id}")
def get_walkin_token(
    token_id: int,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskWalkInService(db).get_walkin_token(token_id)
    return success_response("Walk-in token fetched successfully.", data.model_dump())


@router.post("/walkin-tokens/{token_id}/status")
def update_walkin_token_status(
    token_id: int,
    payload: FrontdeskWalkInStatusUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskWalkInService(db).update_walkin_status(token_id=token_id, payload=payload, actor_user_id=current_user.user_id)
    return success_response("Walk-in token status updated successfully.", data.model_dump())
