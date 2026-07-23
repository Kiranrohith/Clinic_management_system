from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.appointment import Appointment, WaitingList
from app.models.enums import AppointmentStatus, SlotStatus, WaitingStatus
from app.models.patient import Patient
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import User


class FrontdeskAppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_appointment_rows(
        self,
        doctor_user_id: int | None,
        appointment_date: date,
    ) -> list[tuple[Appointment, DoctorAvailability, Slot, Patient, User]]:
        doctor_user = aliased(User)
        stmt = (
            select(Appointment, DoctorAvailability, Slot, Patient, doctor_user)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(Patient, Patient.patient_id == Appointment.patient_id)
            .join(doctor_user, doctor_user.user_id == DoctorAvailability.doctor_user_id)
            .where(DoctorAvailability.available_date == appointment_date)
            .order_by(Slot.slot_start_time.asc(), Appointment.appointment_id.asc())
        )
        if doctor_user_id is not None:
            stmt = stmt.where(DoctorAvailability.doctor_user_id == doctor_user_id)
        return list(self.db.execute(stmt).all())

    def get_appointment_row(
        self,
        appointment_id: int,
    ) -> tuple[Appointment, DoctorAvailability, Slot, Patient, User] | None:
        doctor_user = aliased(User)
        stmt = (
            select(Appointment, DoctorAvailability, Slot, Patient, doctor_user)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(Patient, Patient.patient_id == Appointment.patient_id)
            .join(doctor_user, doctor_user.user_id == DoctorAvailability.doctor_user_id)
            .where(Appointment.appointment_id == appointment_id)
        )
        return self.db.execute(stmt).one_or_none()

    def get_appointment_by_availability_id(self, availability_id: int) -> Appointment | None:
        stmt = select(Appointment).where(Appointment.availability_id == availability_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_appointment_for_update(self, appointment_id: int) -> Appointment | None:
        stmt = select(Appointment).where(Appointment.appointment_id == appointment_id).with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def create_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def save_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def get_availability_for_update(self, availability_id: int) -> DoctorAvailability | None:
        stmt = (
            select(DoctorAvailability)
            .where(DoctorAvailability.availability_id == availability_id)
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_availability(self, availability: DoctorAvailability) -> None:
        self.db.add(availability)
        self.db.flush()

    def get_next_waiting_entry_for_update(self, availability_id: int) -> WaitingList | None:
        stmt = (
            select(WaitingList)
            .where(
                WaitingList.availability_id == availability_id,
                WaitingList.status == WaitingStatus.WAITING,
            )
            .order_by(WaitingList.position.asc())
            .with_for_update()
        )
        return self.db.execute(stmt).scalars().first()

    def save_waiting_entry(self, waiting: WaitingList) -> WaitingList:
        self.db.add(waiting)
        self.db.flush()
        return waiting

    def count_patient_appointments_on_date(self, patient_id: int, target_date: date) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                Appointment.patient_id == patient_id,
                DoctorAvailability.available_date == target_date,
                Appointment.appointment_status.in_(
                    [AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW]
                ),
            )
        )
        return int(self.db.scalar(stmt) or 0)
