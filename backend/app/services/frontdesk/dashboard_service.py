import logging
from datetime import date

from sqlalchemy.orm import Session

from app.repositories.frontdesk.dashboard_repository import FrontdeskDashboardRepository
from app.schemas.frontdesk.dashboard import FrontdeskDashboardResponse
from app.schemas.frontdesk.availability import FrontdeskDoctorOptionResponse

logger = logging.getLogger("clinic.frontdesk")


class FrontdeskDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FrontdeskDashboardRepository(db)

    def get_dashboard(self, doctor_user_id: int | None) -> FrontdeskDashboardResponse:
        counts = self.repo.get_dashboard_counts(target_date=date.today(), doctor_user_id=doctor_user_id)
        return FrontdeskDashboardResponse(**counts)

    def list_doctors(self) -> list[FrontdeskDoctorOptionResponse]:
        rows = self.repo.list_doctor_rows()
        doctors_map: dict[int, FrontdeskDoctorOptionResponse] = {}
        for doctor, user, specialization_id, specialization_name in rows:
            existing = doctors_map.get(doctor.doctor_user_id)
            if existing is None:
                existing = FrontdeskDoctorOptionResponse(
                    doctor_user_id=doctor.doctor_user_id,
                    doctor_name=user.full_name,
                    specializations=[],
                )
                doctors_map[doctor.doctor_user_id] = existing
            if specialization_id is not None and specialization_name is not None:
                if specialization_name not in existing.specializations:
                    existing.specializations.append(specialization_name)
        return list(doctors_map.values())
