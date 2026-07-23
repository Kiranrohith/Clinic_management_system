import logging
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN, ROLE_FRONTDESK
from app.models.enums import NotificationType, SlotStatus, WaitingStatus
from app.models.schedule import DoctorAvailability
from app.repositories.doctor.availability_repository import DoctorAvailabilityRepository
from app.repositories.doctor.appointment_repository import DoctorAppointmentRepository
from app.services.admin.slot_service import AdminSlotService
from app.services.notification_service import NotificationService
from app.services.communication_service import CommunicationService
from app.schemas.doctor.availability import (
    DoctorAvailabilityCreateRequest,
    DoctorAvailabilityTimeWindowRequest,
    DoctorAvailabilityCancelRequest,
    DoctorAvailabilityResponse,
    DoctorAvailabilityTimeWindowResponse,
    DoctorSlotOptionResponse,
    DoctorEmergencyCancelRequest,
    DoctorEmergencyCancelResponse,
)
from app.schemas.doctor.appointment import DoctorAppointmentResponse

logger = logging.getLogger("clinic.doctor")


class DoctorAvailabilityService:
    def __init__(self, db: Session):
        self.db = db
        self.avail_repo = DoctorAvailabilityRepository(db)
        self.appt_repo = DoctorAppointmentRepository(db)
        self.notification_service = NotificationService(db)
        self.communication_service = CommunicationService()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _today() -> date:
        return date.today()

    @classmethod
    def _validate_five_day_window(cls, target_date: date) -> None:
        start_date = cls._today()
        end_date = start_date + timedelta(days=4)
        if target_date < start_date or target_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor availability can only be managed within the next five days.",
            )

    @staticmethod
    def _slot_within_window(slot_start, slot_end, start_time, end_time) -> bool:
        return slot_start >= start_time and slot_end <= end_time

    def _list_effective_slots(self):
        return AdminSlotService(self.db).list_slots()

    def list_availabilities(
        self,
        doctor_user_id: int,
        available_date: date | None,
    ) -> list[DoctorAvailabilityResponse]:
        effective_slot_ids = {slot.slot_id for slot in self._list_effective_slots()}
        rows = self.avail_repo.list_availability_rows(doctor_user_id=doctor_user_id, available_date=available_date)
        return [
            DoctorAvailabilityResponse(
                availability_id=a.availability_id,
                available_date=a.available_date,
                slot_id=a.slot_id,
                slot_start_time=slot.slot_start_time,
                slot_end_time=slot.slot_end_time,
                slot_status=a.slot_status,
                cancellation_reason=a.cancellation_reason,
            )
            for a, slot in rows
            if slot.slot_id in effective_slot_ids
        ]

    def list_slots(self) -> list[DoctorSlotOptionResponse]:
        slots = self._list_effective_slots()
        return [
            DoctorSlotOptionResponse(slot_id=s.slot_id, slot_start_time=s.slot_start_time, slot_end_time=s.slot_end_time)
            for s in slots
        ]

    def create_availability(
        self,
        doctor_user_id: int,
        payload: DoctorAvailabilityCreateRequest,
    ) -> DoctorAvailabilityResponse:
        now = self._now()
        self._validate_five_day_window(payload.available_date)
        slot = self.avail_repo.get_slot(payload.slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
        existing = self.avail_repo.get_availability_conflict(
            doctor_user_id=doctor_user_id,
            available_date=payload.available_date,
            slot_id=payload.slot_id,
        )
        if existing is not None:
            if existing.slot_status in {SlotStatus.CANCELLED_BY_DOCTOR, SlotStatus.BLOCKED}:
                existing.slot_status = SlotStatus.AVAILABLE
                existing.cancellation_reason = None
                existing.updated_by = doctor_user_id
                existing.updated_at = now
                restored = self.avail_repo.save_availability(existing)
                return DoctorAvailabilityResponse(
                    availability_id=restored.availability_id,
                    available_date=restored.available_date,
                    slot_id=restored.slot_id,
                    slot_start_time=slot.slot_start_time,
                    slot_end_time=slot.slot_end_time,
                    slot_status=restored.slot_status,
                    cancellation_reason=restored.cancellation_reason,
                )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Availability already exists for this date and slot.")
        availability = DoctorAvailability(
            doctor_user_id=doctor_user_id,
            available_date=payload.available_date,
            slot_id=payload.slot_id,
            slot_status=SlotStatus.AVAILABLE,
            created_by=doctor_user_id,
            updated_by=doctor_user_id,
            created_at=now,
            updated_at=now,
        )
        try:
            created = self.avail_repo.create_availability(availability)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create availability due to conflict.") from exc
        return DoctorAvailabilityResponse(
            availability_id=created.availability_id,
            available_date=created.available_date,
            slot_id=created.slot_id,
            slot_start_time=slot.slot_start_time,
            slot_end_time=slot.slot_end_time,
            slot_status=created.slot_status,
            cancellation_reason=created.cancellation_reason,
        )

    def apply_availability_time_window(
        self,
        doctor_user_id: int,
        payload: DoctorAvailabilityTimeWindowRequest,
    ) -> DoctorAvailabilityTimeWindowResponse:
        self._validate_five_day_window(payload.available_date)
        if payload.start_time >= payload.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be earlier than end time.")
        now = self._now()
        slots = self._list_effective_slots()
        if not slots:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No slots configured.")
        existing_rows = self.avail_repo.list_availabilities_for_date(doctor_user_id=doctor_user_id, available_date=payload.available_date)
        existing_by_slot_id = {row.slot_id: row for row in existing_rows}
        enabled_count = 0
        disabled_count = 0
        skipped_booked_count = 0
        with self.db.begin_nested():
            for slot in slots:
                availability = existing_by_slot_id.get(slot.slot_id)
                inside_window = self._slot_within_window(slot.slot_start_time, slot.slot_end_time, payload.start_time, payload.end_time)
                if inside_window:
                    if availability is None:
                        created = self.avail_repo.create_availability(
                            DoctorAvailability(
                                doctor_user_id=doctor_user_id,
                                available_date=payload.available_date,
                                slot_id=slot.slot_id,
                                slot_status=SlotStatus.AVAILABLE,
                                cancellation_reason=None,
                                created_by=doctor_user_id,
                                updated_by=doctor_user_id,
                                created_at=now,
                                updated_at=now,
                            )
                        )
                        existing_by_slot_id[slot.slot_id] = created
                    else:
                        if availability.slot_status != SlotStatus.BOOKED:
                            availability.slot_status = SlotStatus.AVAILABLE
                            availability.cancellation_reason = None
                            availability.updated_by = doctor_user_id
                            availability.updated_at = now
                            self.avail_repo.save_availability(availability)
                    enabled_count += 1
                    continue
                if availability is None:
                    self.avail_repo.create_availability(
                        DoctorAvailability(
                            doctor_user_id=doctor_user_id,
                            available_date=payload.available_date,
                            slot_id=slot.slot_id,
                            slot_status=SlotStatus.BLOCKED,
                            cancellation_reason=None,
                            created_by=doctor_user_id,
                            updated_by=doctor_user_id,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    disabled_count += 1
                    continue
                if availability.slot_status == SlotStatus.BOOKED:
                    skipped_booked_count += 1
                    continue
                availability.slot_status = SlotStatus.BLOCKED
                availability.cancellation_reason = None
                availability.updated_by = doctor_user_id
                availability.updated_at = now
                self.avail_repo.save_availability(availability)
                disabled_count += 1
        return DoctorAvailabilityTimeWindowResponse(
            available_date=payload.available_date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            enabled_count=enabled_count,
            disabled_count=disabled_count,
            skipped_booked_count=skipped_booked_count,
        )

    def cancel_availability(
        self,
        doctor_user_id: int,
        availability_id: int,
        payload: DoctorAvailabilityCancelRequest,
    ) -> DoctorAvailabilityResponse:
        now = self._now()
        with self.db.begin_nested():
            availability = self.avail_repo.get_availability_for_update(
                availability_id=availability_id,
                doctor_user_id=doctor_user_id,
            )
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            self._validate_five_day_window(availability.available_date)
            booked_appointment = self.appt_repo.get_booked_appointment_for_availability_for_update(availability.availability_id)
            if booked_appointment is not None:
                booked_appointment.appointment_status = __import__('app.models.enums', fromlist=['AppointmentStatus']).AppointmentStatus.CANCELLED_BY_DOCTOR
                booked_appointment.cancellation_reason = payload.cancellation_reason.strip()
                booked_appointment.updated_by = doctor_user_id
                booked_appointment.updated_at = now
                self.appt_repo.save_appointment(booked_appointment)
            waiting_entries = self.appt_repo.list_waiting_entries_for_update(availability.availability_id)
            for waiting in waiting_entries:
                waiting.status = WaitingStatus.CANCELLED
                waiting.updated_at = now
                self.appt_repo.save_waiting_entry(waiting)
            availability.slot_status = SlotStatus.CANCELLED_BY_DOCTOR
            availability.cancellation_reason = payload.cancellation_reason.strip()
            availability.updated_by = doctor_user_id
            availability.updated_at = now
            self.avail_repo.save_availability(availability)
        slot = self.avail_repo.get_slot(availability.slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
        logger.info("Doctor cancelled availability availability_id=%s doctor_user_id=%s", availability.availability_id, doctor_user_id)
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK, ROLE_ADMIN),
            notification_type=NotificationType.DOCTOR_EMERGENCY,
            title="Doctor availability cancelled",
            message=f"Doctor cancelled availability #{availability.availability_id}.",
            metadata={"availability_id": availability.availability_id},
        )
        return DoctorAvailabilityResponse(
            availability_id=availability.availability_id,
            available_date=availability.available_date,
            slot_id=availability.slot_id,
            slot_start_time=slot.slot_start_time,
            slot_end_time=slot.slot_end_time,
            slot_status=availability.slot_status,
            cancellation_reason=availability.cancellation_reason,
        )

    def emergency_cancel_remaining(
        self,
        doctor_user_id: int,
        payload: DoctorEmergencyCancelRequest,
    ) -> DoctorEmergencyCancelResponse:
        self._validate_five_day_window(payload.available_date)
        slot = self.avail_repo.get_slot(payload.from_slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
        reason = payload.cancellation_reason.strip()
        now = self._now()
        rows = self.avail_repo.list_availability_rows_from_slot(
            doctor_user_id=doctor_user_id,
            available_date=payload.available_date,
            slot_start_time=slot.slot_start_time,
        )
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No availability found for the selected range.")
        from app.models.enums import AppointmentStatus
        cancelled_availability_ids: list[int] = []
        cancelled_appointment_ids: list[int] = []
        sms_notifications: list[tuple] = []
        with self.db.begin_nested():
            for availability, availability_slot in rows:
                if availability.slot_status == SlotStatus.CANCELLED_BY_DOCTOR:
                    continue
                booked_appointment = self.appt_repo.get_booked_appointment_for_availability_for_update(availability.availability_id)
                if booked_appointment is not None:
                    booked_appointment.appointment_status = AppointmentStatus.CANCELLED_BY_DOCTOR
                    booked_appointment.cancellation_reason = reason
                    booked_appointment.updated_by = doctor_user_id
                    booked_appointment.updated_at = now
                    self.appt_repo.save_appointment(booked_appointment)
                    cancelled_appointment_ids.append(booked_appointment.appointment_id)
                    appointment_row = self.appt_repo.get_appointment_row(
                        doctor_user_id=doctor_user_id,
                        appointment_id=booked_appointment.appointment_id,
                    )
                    if appointment_row is not None:
                        _, _, _, patient = appointment_row
                        sms_notifications.append((patient.phone, booked_appointment.appointment_id, availability.available_date, availability_slot.slot_start_time.strftime("%H:%M")))
                availability.slot_status = SlotStatus.CANCELLED_BY_DOCTOR
                availability.cancellation_reason = reason
                availability.updated_by = doctor_user_id
                availability.updated_at = now
                self.avail_repo.save_availability(availability)
                cancelled_availability_ids.append(availability.availability_id)
        for phone, appointment_id, available_date, slot_time in sms_notifications:
            self.communication_service.send_sms(
                phone=phone,
                template_key="DOCTOR_EMERGENCY_RESCHEDULE",
                variables={"appointment_id": str(appointment_id), "date": str(available_date), "time": slot_time, "reschedule_path": "/bookings"},
            )
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK, ROLE_ADMIN),
            notification_type=NotificationType.DOCTOR_EMERGENCY,
            title="Doctor cancelled remaining slots",
            message=f"Doctor cancelled remaining slots on {payload.available_date} from {slot.slot_start_time.strftime('%H:%M')} onward.",
            metadata={"available_date": str(payload.available_date), "from_slot_id": payload.from_slot_id, "cancelled_appointment_ids": cancelled_appointment_ids},
        )
        return DoctorEmergencyCancelResponse(
            available_date=payload.available_date,
            from_slot_id=payload.from_slot_id,
            cancelled_availability_ids=cancelled_availability_ids,
            cancelled_appointment_ids=cancelled_appointment_ids,
        )
