from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.services.frontdesk.dashboard_service import FrontdeskDashboardService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.get("/dashboard")
def frontdesk_dashboard(
    doctor_user_id: int | None = None,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskDashboardService(db).get_dashboard(doctor_user_id=doctor_user_id)
    return success_response("Frontdesk dashboard data fetched.", data.model_dump())


@router.get("/doctors")
def list_doctors(
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskDashboardService(db).list_doctors()
    return success_response("Doctors fetched successfully.", [item.model_dump() for item in data])
