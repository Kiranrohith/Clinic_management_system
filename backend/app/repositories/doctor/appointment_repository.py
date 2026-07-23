from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, WaitingList
from app.models.enums import AppointmentStatus, WaitingStatus
from app.models.patient import Patient
from app.models.schedule import DoctorAvailability, Slot


class DoctorAppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_appointment_rows(
        self,
        doctor_user_id: int,
        available_date: date | None,
        appointment_status: AppointmentStatus | None,
    ) -> list[tuple[Appointment, DoctorAvailability, Slot, Patient]]:
        stmt = (
            select(Appointment, DoctorAvailability, Slot, Patient)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(Patient, Patient.patient_id == Appointment.patient_id)
            .where(DoctorAvailability.doctor_user_id == doctor_user_id)
            .order_by(DoctorAvailability.available_date.asc(), Slot.slot_start_time.asc())
        )
        if available_date is not None:
            stmt = stmt.where(DoctorAvailability.available_date == available_date)
        if appointment_status is not None:
            stmt = stmt.where(Appointment.appointment_status == appointment_status)
        return list(self.db.execute(stmt).all())

    def get_appointment_row(
        self,
        doctor_user_id: int,
        appointment_id: int,
    ) -> tuple[Appointment, DoctorAvailability, Slot, Patient] | None:
        stmt = (
            select(Appointment, DoctorAvailability, Slot, Patient)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(Patient, Patient.patient_id == Appointment.patient_id)
            .where(
                DoctorAvailability.doctor_user_id == doctor_user_id,
                Appointment.appointment_id == appointment_id,
            )
        )
        return self.db.execute(stmt).one_or_none()

    def get_appointment_for_update(
        self,
        doctor_user_id: int,
        appointment_id: int,
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                Appointment.appointment_id == appointment_id,
                DoctorAvailability.doctor_user_id == doctor_user_id,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_booked_appointment_for_availability_for_update(
        self,
        availability_id: int,
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .where(
                Appointment.availability_id == availability_id,
                Appointment.appointment_status == AppointmentStatus.BOOKED,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def list_waiting_entries_for_update(self, availability_id: int) -> list[WaitingList]:
        stmt = (
            select(WaitingList)
            .where(
                WaitingList.availability_id == availability_id,
                WaitingList.status.in_([WaitingStatus.WAITING, WaitingStatus.NOTIFIED, WaitingStatus.CONFIRMED]),
            )
            .with_for_update()
        )
        return list(self.db.execute(stmt).scalars().all())

    def save_waiting_entry(self, waiting: WaitingList) -> WaitingList:
        self.db.add(waiting)
        self.db.flush()
        return waiting
