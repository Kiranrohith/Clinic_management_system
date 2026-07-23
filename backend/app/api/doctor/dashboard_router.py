from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_DOCTOR
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.services.doctor.dashboard_service import DoctorDashboardService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])


@router.get("/dashboard")
def doctor_dashboard(
    current_user: User = Depends(require_roles(ROLE_DOCTOR)),
    db: Session = Depends(get_db),
):
    data = DoctorDashboardService(db).get_dashboard(current_user.user_id)
    return success_response("Doctor dashboard data fetched.", data.model_dump())
