from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import Role, User


class AdminDashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_counts(self) -> dict[str, int]:
        management_users_count = self.db.scalar(
            select(func.count()).select_from(User).join(Role, User.role_id == Role.role_id)
            .where(Role.role_name.in_(("ADMIN", "DOCTOR", "FRONTDESK")))
        ) or 0
        doctors_count = self.db.scalar(select(func.count()).select_from(Doctor)) or 0
        frontdesk_count = self.db.scalar(
            select(func.count()).select_from(User).join(Role, User.role_id == Role.role_id)
            .where(Role.role_name == "FRONTDESK")
        ) or 0
        patients_count = self.db.scalar(select(func.count()).select_from(Patient)) or 0
        appointments_count = self.db.scalar(select(func.count()).select_from(Appointment)) or 0
        return {
            "management_users": int(management_users_count),
            "doctors": int(doctors_count),
            "frontdesk": int(frontdesk_count),
            "patients": int(patients_count),
            "appointments": int(appointments_count),
        }
