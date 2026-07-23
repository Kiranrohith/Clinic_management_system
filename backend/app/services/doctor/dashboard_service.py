from datetime import date
from sqlalchemy.orm import Session

from app.repositories.doctor.dashboard_repository import DoctorDashboardRepository
from app.schemas.doctor.dashboard import DoctorDashboardResponse


class DoctorDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DoctorDashboardRepository(db)

    def get_dashboard(self, doctor_user_id: int) -> DoctorDashboardResponse:
        counts = self.repo.get_dashboard_counts(doctor_user_id=doctor_user_id, target_date=date.today())
        return DoctorDashboardResponse(**counts)
