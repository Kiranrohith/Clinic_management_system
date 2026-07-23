import logging
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.models.appointment import Appointment
from app.models.enums import (
    AppointmentStatus,
    BookingSource,
    NotificationType,
    SlotStatus,
    WaitingStatus,
)
from app.repositories.frontdesk.appointment_repository import FrontdeskAppointmentRepository
from app.repositories.frontdesk.availability_repository import FrontdeskAvailabilityRepository
from app.repositories.frontdesk.patient_repository import FrontdeskPatientRepository
from app.services.admin.slot_service import AdminSlotService
from app.services.notification_service import NotificationService
from app.schemas.frontdesk.appointment import (
    FrontdeskAppointmentListItemResponse,
    FrontdeskAppointmentResponse,
    FrontdeskBookAppointmentRequest,
    FrontdeskCancelAppointmentRequest,
)
from app.schemas.frontdesk.availability import FrontdeskAvailabilityResponse

logger = logging.getLogger("clinic.frontdesk")


class FrontdeskAppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.appt_repo = FrontdeskAppointmentRepository(db)
        self.avail_repo = FrontdeskAvailabilityRepository(db)
        self.patient_repo = FrontdeskPatientRepository(db)
        self.notification_service = NotificationService(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def _effective_slot_ids(self) -> set[int]:
        return {slot.slot_id for slot in AdminSlotService(self.db).list_slots()}

    def list_availabilities(
        self,
        doctor_user_id: int | None,
        available_date: date | None,
    ) -> list[FrontdeskAvailabilityResponse]:
        effective_slot_ids = self._effective_slot_ids()
        rows = self.avail_repo.list_available_rows(doctor_user_id=doctor_user_id, available_date=available_date)
        return [
            FrontdeskAvailabilityResponse(
                availability_id=availability.availability_id,
                doctor_user_id=availability.doctor_user_id,
                doctor_name=user.full_name,
                available_date=availability.available_date,
                slot_id=slot.slot_id,
                slot_start_time=slot.slot_start_time,
                slot_end_time=slot.slot_end_time,
                slot_status=availability.slot_status.value,
            )
            for availability, slot, user in rows
            if slot.slot_id in effective_slot_ids
        ]

    def list_appointments(
        self,
        appointment_date: date,
        doctor_user_id: int | None,
    ) -> list[FrontdeskAppointmentListItemResponse]:
        rows = self.appt_repo.list_appointment_rows(doctor_user_id=doctor_user_id, appointment_date=appointment_date)
        return [
            FrontdeskAppointmentListItemResponse(
                appointment_id=appointment.appointment_id,
                patient_id=patient.patient_id,
                patient_name=patient.full_name,
                patient_phone=patient.phone,
                doctor_user_id=availability.doctor_user_id,
                doctor_name=doctor_user.full_name,
                availability_id=availability.availability_id,
                appointment_date=availability.available_date,
                slot_start_time=slot.slot_start_time,
                slot_end_time=slot.slot_end_time,
                appointment_status=appointment.appointment_status.value,
                booking_source=appointment.booking_source.value if appointment.booking_source else None,
                cancellation_reason=appointment.cancellation_reason,
                created_at=appointment.created_at,
                updated_at=appointment.updated_at,
            )
            for appointment, availability, slot, patient, doctor_user in rows
        ]

    def get_appointment(self, appointment_id: int) -> FrontdeskAppointmentListItemResponse:
        row = self.appt_repo.get_appointment_row(appointment_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
        appointment, availability, slot, patient, doctor_user = row
        return FrontdeskAppointmentListItemResponse(
            appointment_id=appointment.appointment_id,
            patient_id=patient.patient_id,
            patient_name=patient.full_name,
            patient_phone=patient.phone,
            doctor_user_id=availability.doctor_user_id,
            doctor_name=doctor_user.full_name,
            availability_id=availability.availability_id,
            appointment_date=availability.available_date,
            slot_start_time=slot.slot_start_time,
            slot_end_time=slot.slot_end_time,
            appointment_status=appointment.appointment_status.value,
            booking_source=appointment.booking_source.value if appointment.booking_source else None,
            cancellation_reason=appointment.cancellation_reason,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
        )

    def book_appointment(
        self,
        payload: FrontdeskBookAppointmentRequest,
        actor_user_id: int,
    ) -> FrontdeskAppointmentResponse:
        now = self._now()
        patient = self.patient_repo.get_patient_by_phone(payload.patient_phone.strip())
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

        with self.db.begin_nested():
            availability = self.avail_repo.get_availability_for_update(payload.availability_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            if availability.slot_id not in self._effective_slot_ids():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected slot is no longer valid for current clinic schedule.")
            if availability.slot_status != SlotStatus.AVAILABLE:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected slot is not available.")
            if self.appt_repo.get_appointment_by_availability_id(payload.availability_id) is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment already exists for this availability.")

            clinic_settings = self.appt_repo.get_clinic_settings()
            appointment_limit_per_day = clinic_settings.appointment_limit_per_day if clinic_settings else 2
            booked_count = self.appt_repo.count_patient_appointments_on_date(
                patient_id=patient.patient_id,
                target_date=availability.available_date,
            )
            if booked_count >= appointment_limit_per_day:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient daily appointment limit reached.")

            appointment = Appointment(
                patient_id=patient.patient_id,
                availability_id=availability.availability_id,
                booking_source=BookingSource.FRONTDESK,
                appointment_status=AppointmentStatus.BOOKED,
                booked_by_phone=patient.phone,
                booked_by_user_id=actor_user_id,
                created_by=actor_user_id,
                updated_by=actor_user_id,
                created_at=now,
                updated_at=now,
            )
            try:
                created = self.appt_repo.create_appointment(appointment)
            except IntegrityError as exc:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create appointment due to conflicting data.") from exc

            availability.slot_status = SlotStatus.BOOKED
            availability.updated_by = actor_user_id
            availability.updated_at = now
            self.avail_repo.save_availability(availability)

        logger.info("Frontdesk booked appointment appointment_id=%s patient_id=%s by_user_id=%s", created.appointment_id, created.patient_id, actor_user_id)
        self.notification_service.create_for_user(
            user_id=availability.doctor_user_id,
            notification_type=NotificationType.APPOINTMENT_BOOKED,
            title="New frontdesk booking",
            message=f"Appointment #{created.appointment_id} was booked by frontdesk.",
            metadata={"appointment_id": created.appointment_id},
        )
        return FrontdeskAppointmentResponse(
            appointment_id=created.appointment_id,
            patient_id=created.patient_id,
            availability_id=created.availability_id,
            appointment_status=created.appointment_status.value,
            booking_source=created.booking_source.value,
        )

    def cancel_appointment(
        self,
        appointment_id: int,
        payload: FrontdeskCancelAppointmentRequest,
        actor_user_id: int,
    ) -> FrontdeskAppointmentResponse:
        now = self._now()
        next_waiting = None
        with self.db.begin_nested():
            appointment = self.appt_repo.get_appointment_for_update(appointment_id)
            if appointment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
            if appointment.appointment_status != AppointmentStatus.BOOKED:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only BOOKED appointments can be cancelled by frontdesk.")

            availability = self.avail_repo.get_availability_for_update(appointment.availability_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")

            appointment.appointment_status = AppointmentStatus.CANCELLED_BY_FRONTDESK
            appointment.cancellation_reason = payload.cancellation_reason.strip()
            appointment.updated_by = actor_user_id
            appointment.updated_at = now
            self.appt_repo.save_appointment(appointment)

            next_waiting = self.appt_repo.get_next_waiting_entry_for_update(appointment.availability_id)
            if next_waiting is None:
                availability.slot_status = SlotStatus.AVAILABLE
            else:
                next_waiting.status = WaitingStatus.NOTIFIED
                next_waiting.notified_at = now
                next_waiting.expires_at = now + timedelta(minutes=15)
                next_waiting.updated_at = now
                self.appt_repo.save_waiting_entry(next_waiting)
                availability.slot_status = SlotStatus.BLOCKED

            availability.updated_by = actor_user_id
            availability.updated_at = now
            self.avail_repo.save_availability(availability)

        logger.info("Frontdesk cancelled appointment appointment_id=%s by_user_id=%s", appointment.appointment_id, actor_user_id)
        self.notification_service.create_for_user(
            user_id=availability.doctor_user_id,
            notification_type=NotificationType.APPOINTMENT_CANCELLED,
            title="Appointment cancelled",
            message=f"Appointment #{appointment.appointment_id} was cancelled by frontdesk.",
            metadata={"appointment_id": appointment.appointment_id},
        )
        if next_waiting is not None:
            self.notification_service.create_for_roles(
                role_names=(ROLE_ADMIN,),
                notification_type=NotificationType.WAITING_LIST_AVAILABLE,
                title="Waiting list promotion required",
                message=f"Waiting entry #{next_waiting.waiting_id} has been notified.",
                metadata={"waiting_id": next_waiting.waiting_id, "availability_id": next_waiting.availability_id},
            )
        return FrontdeskAppointmentResponse(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            availability_id=appointment.availability_id,
            appointment_status=appointment.appointment_status.value,
            booking_source=appointment.booking_source.value if appointment.booking_source else "",
        )
