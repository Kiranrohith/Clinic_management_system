from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, WaitingList
from app.models.clinic import ClinicSetting
from app.models.enums import AppointmentStatus, SlotStatus, WaitingStatus
from app.models.patient import Patient
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import User


class PublicBookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_availability_for_booking(self, availability_id: int) -> DoctorAvailability | None:
        stmt = (
            select(DoctorAvailability)
            .where(DoctorAvailability.availability_id == availability_id)
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_appointment_by_availability_id(self, availability_id: int) -> Appointment | None:
        stmt = select(Appointment).where(Appointment.availability_id == availability_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_patient_by_phone(self, phone: str) -> Patient | None:
        stmt = select(Patient).where(Patient.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def create_patient(
        self,
        full_name: str,
        phone: str,
        gender,
        dob,
        blood_group: str | None,
        address: str | None,
        emergency_contact: str | None,
        now: datetime,
    ) -> Patient:
        patient = Patient(
            full_name=full_name,
            phone=phone,
            gender=gender,
            dob=dob,
            blood_group=blood_group,
            address=address,
            emergency_contact=emergency_contact,
            created_at=now,
            updated_at=now,
        )
        self.db.add(patient)
        self.db.flush()
        return patient

    def count_patient_appointments_on_date(self, patient_id: int, target_date: date) -> int:
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

    def count_patient_appointments_on_date_excluding(
        self,
        patient_id: int,
        target_date: date,
        exclude_appointment_id: int,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Appointment)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.appointment_id != exclude_appointment_id,
                DoctorAvailability.available_date == target_date,
                Appointment.appointment_status.in_(
                    [AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW]
                ),
            )
        )
        return int(self.db.scalar(stmt) or 0)

    def get_clinic_settings(self) -> ClinicSetting | None:
        stmt = select(ClinicSetting).where(ClinicSetting.id == 1)
        return self.db.execute(stmt).scalar_one_or_none()

    def create_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def update_availability(self, availability: DoctorAvailability) -> None:
        self.db.add(availability)
        self.db.flush()

    def save_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def get_appointment_for_update_by_booked_phone(
        self,
        appointment_id: int,
        booked_by_phone: str,
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .where(
                Appointment.appointment_id == appointment_id,
                Appointment.booked_by_phone == booked_by_phone,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_appointment_rows_by_booked_phone(
        self,
        booked_by_phone: str,
    ) -> list[tuple[Appointment, Patient, DoctorAvailability, Slot, User]]:
        stmt = (
            select(Appointment, Patient, DoctorAvailability, Slot, User)
            .join(Patient, Patient.patient_id == Appointment.patient_id)
            .join(DoctorAvailability, DoctorAvailability.availability_id == Appointment.availability_id)
            .join(Slot, Slot.slot_id == DoctorAvailability.slot_id)
            .join(User, User.user_id == DoctorAvailability.doctor_user_id)
            .where(Appointment.booked_by_phone == booked_by_phone)
            .order_by(DoctorAvailability.available_date.desc(), Slot.slot_start_time.desc())
        )
        return list(self.db.execute(stmt).all())

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

    def get_waiting_entry(self, patient_id: int, availability_id: int) -> WaitingList | None:
        stmt = select(WaitingList).where(
            WaitingList.patient_id == patient_id,
            WaitingList.availability_id == availability_id,
            WaitingList.status.in_([WaitingStatus.WAITING, WaitingStatus.NOTIFIED, WaitingStatus.CONFIRMED]),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_next_waiting_position(self, availability_id: int) -> int:
        stmt = select(func.max(WaitingList.position)).where(WaitingList.availability_id == availability_id)
        max_position = self.db.scalar(stmt)
        return int(max_position or 0) + 1

    def create_waiting_entry(self, entry: WaitingList) -> WaitingList:
        self.db.add(entry)
        self.db.flush()
        return entry
