from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, WalkInToken
from app.models.enums import AppointmentStatus
from app.models.schedule import DoctorAvailability


class DoctorDashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_counts(self, doctor_user_id: int, target_date: date) -> dict[str, int]:
        todays_appointments = self.db.scalar(
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                DoctorAvailability.doctor_user_id == doctor_user_id,
                DoctorAvailability.available_date == target_date,
            )
        )
        completed_appointments = self.db.scalar(
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                DoctorAvailability.doctor_user_id == doctor_user_id,
                DoctorAvailability.available_date == target_date,
                Appointment.appointment_status == AppointmentStatus.COMPLETED,
            )
        )
        pending_appointments = self.db.scalar(
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                DoctorAvailability.doctor_user_id == doctor_user_id,
                DoctorAvailability.available_date == target_date,
                Appointment.appointment_status == AppointmentStatus.BOOKED,
            )
        )
        todays_walkin = self.db.scalar(
            select(func.count())
            .select_from(WalkInToken)
            .where(
                WalkInToken.doctor_user_id == doctor_user_id,
                WalkInToken.token_date == target_date,
            )
        )
        return {
            "todays_appointments": int(todays_appointments or 0),
            "completed_appointments": int(completed_appointments or 0),
            "pending_appointments": int(pending_appointments or 0),
            "todays_walkin_tokens": int(todays_walkin or 0),
        }
