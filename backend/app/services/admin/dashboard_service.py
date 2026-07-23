from sqlalchemy.orm import Session

from app.repositories.admin.dashboard_repository import AdminDashboardRepository
from app.schemas.admin.dashboard import AdminDashboardResponse


class AdminDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminDashboardRepository(db)

    def get_dashboard(self) -> AdminDashboardResponse:
        counts = self.repo.get_dashboard_counts()
        return AdminDashboardResponse(**counts)
