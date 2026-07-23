from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, WaitingList, WalkInToken
from app.models.enums import WaitingStatus
from app.models.schedule import DoctorAvailability

from app.models.clinic import ClinicSetting


class FrontdeskDashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_clinic_settings(self) -> ClinicSetting | None:
        stmt = select(ClinicSetting).where(ClinicSetting.id == 1)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_dashboard_counts(self, target_date: date, doctor_user_id: int | None) -> dict[str, int]:
        appointment_stmt = (
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(DoctorAvailability.available_date == target_date)
        )
        walkin_stmt = select(func.count()).select_from(WalkInToken).where(WalkInToken.token_date == target_date)
        waiting_stmt = (
            select(func.count())
            .select_from(WaitingList)
            .join(DoctorAvailability, DoctorAvailability.availability_id == WaitingList.availability_id)
            .where(
                WaitingList.status == WaitingStatus.WAITING,
                DoctorAvailability.available_date == target_date,
            )
        )
        if doctor_user_id is not None:
            appointment_stmt = appointment_stmt.where(DoctorAvailability.doctor_user_id == doctor_user_id)
            walkin_stmt = walkin_stmt.where(WalkInToken.doctor_user_id == doctor_user_id)
            waiting_stmt = waiting_stmt.where(DoctorAvailability.doctor_user_id == doctor_user_id)

        return {
            "todays_appointments": int(self.db.scalar(appointment_stmt) or 0),
            "todays_walkin_tokens": int(self.db.scalar(walkin_stmt) or 0),
            "waiting_patients": int(self.db.scalar(waiting_stmt) or 0),
        }
