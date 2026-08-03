from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prescription import Prescription
from app.models.appointment import Appointment
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import User


class DoctorPrescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_prescription_by_appointment(
        self,
        doctor_user_id: int,
        appointment_id: int,
    ) -> Prescription | None:
        stmt = select(Prescription).where(
            Prescription.appointment_id == appointment_id,
            Prescription.doctor_user_id == doctor_user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_prescription_history_rows(
        self,
        patient_id: int,
        exclude_appointment_id: int | None = None,
    ) -> list[tuple[Prescription, Appointment, DoctorAvailability, Slot, User]]:
        stmt = (
            select(Prescription, Appointment, DoctorAvailability, Slot, User)
            .join(Appointment, Appointment.appointment_id == Prescription.appointment_id)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(User, User.user_id == Prescription.doctor_user_id)
            .where(Prescription.patient_id == patient_id)
            .order_by(DoctorAvailability.available_date.desc(), Slot.slot_start_time.desc())
        )
        if exclude_appointment_id is not None:
            stmt = stmt.where(Prescription.appointment_id != exclude_appointment_id)
        return list(self.db.execute(stmt).all())

    def create_prescription(self, prescription: Prescription) -> Prescription:
        self.db.add(prescription)
        self.db.flush()
        return prescription

    def save_prescription(self, prescription: Prescription) -> Prescription:
        return self.create_prescription(prescription)
