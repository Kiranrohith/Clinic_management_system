import logging
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.config import settings
from app.core.jwt import create_public_booking_token, decode_public_booking_token
from app.models.appointment import Appointment, WaitingList
from app.models.enums import (
    AppointmentStatus,
    BookingSource,
    NotificationType,
    SlotStatus,
    WaitingStatus,
)
from app.repositories.public.booking_repository import PublicBookingRepository
from app.services.admin.slot_service import AdminSlotService
from app.services.communication_service import CommunicationService
from app.services.notification_service import NotificationService
from app.schemas.public.booking import (
    PublicAppointmentCancelRequest,
    PublicAppointmentHistoryItemResponse,
    PublicAppointmentRescheduleRequest,
    PublicAuthenticatedBookAppointmentRequest,
    PublicBookAppointmentRequest,
    PublicBookAppointmentResponse,
    PublicBookingPatientInput,
    PublicJoinWaitingListRequest,
    PublicJoinWaitingListResponse,
)
from app.schemas.public.patient import PublicPatientProfileResponse

logger = logging.getLogger("clinic.public")


class PublicBookingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PublicBookingRepository(db)
        self.notification_service = NotificationService(db)
        self.communication_service = CommunicationService()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def _effective_slot_ids(self) -> set[int]:
        return {slot.slot_id for slot in AdminSlotService(self.db).list_slots()}

    def _decode_valid_booking_session_phone(self, booking_session_token: str) -> str:
        try:
            payload = decode_public_booking_token(booking_session_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired booking session.") from exc
        phone = payload.get("sub")
        if not isinstance(phone, str) or not phone.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid booking session subject.")
        return phone.strip()

    def _book_appointment_internal(
        self,
        availability_id: int,
        patient_input,
        booked_by_phone: str | None,
    ) -> PublicBookAppointmentResponse:
        now = self._now()
        effective_slot_ids = self._effective_slot_ids()
        with self.db.begin_nested():
            availability = self.repo.get_availability_for_booking(availability_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            if availability.slot_id not in effective_slot_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected slot is no longer valid for current clinic schedule.")
            if availability.slot_status != SlotStatus.AVAILABLE:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected slot is not available.")
            existing_appointment = self.repo.get_appointment_by_availability_id(availability_id)
            if existing_appointment is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment already exists for this availability.")
            patient = self.repo.get_patient_by_phone(patient_input.phone.strip())
            if patient is None:
                patient = self.repo.create_patient(
                    full_name=patient_input.full_name.strip(),
                    phone=patient_input.phone.strip(),
                    gender=patient_input.gender,
                    dob=patient_input.dob,
                    blood_group=patient_input.blood_group,
                    address=patient_input.address,
                    emergency_contact=patient_input.emergency_contact,
                    now=now,
                )
            clinic_settings = self.repo.get_clinic_settings()
            appointment_limit_per_day = clinic_settings.appointment_limit_per_day if clinic_settings else 2
            existing_count = self.repo.count_patient_appointments_on_date(
                patient_id=patient.patient_id,
                target_date=availability.available_date,
            )
            if existing_count >= appointment_limit_per_day:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient daily appointment limit reached.")
            appointment = Appointment(
                patient_id=patient.patient_id,
                availability_id=availability.availability_id,
                booking_source=BookingSource.ONLINE,
                appointment_status=AppointmentStatus.BOOKED,
                booked_by_phone=booked_by_phone or patient.phone,
                created_at=now,
                updated_at=now,
            )
            try:
                created = self.repo.create_appointment(appointment)
                availability.slot_status = SlotStatus.BOOKED
                availability.updated_at = now
                self.repo.update_availability(availability)
            except IntegrityError as exc:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not book appointment due to conflicting data.") from exc

        logger.info("Appointment booked appointment_id=%s patient_id=%s availability_id=%s source=ONLINE", created.appointment_id, created.patient_id, created.availability_id)
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK,),
            notification_type=NotificationType.APPOINTMENT_BOOKED,
            title="New online appointment booked",
            message=f"Appointment #{created.appointment_id} was booked online.",
            metadata={"appointment_id": created.appointment_id, "availability_id": created.availability_id},
        )
        self.notification_service.create_for_user(
            user_id=availability.doctor_user_id,
            notification_type=NotificationType.APPOINTMENT_BOOKED,
            title="New appointment booked",
            message=f"You have a new appointment #{created.appointment_id}.",
            metadata={"appointment_id": created.appointment_id, "availability_id": created.availability_id},
        )
        self.communication_service.send_sms(
            phone=booked_by_phone or patient.phone,
            template_key="APPOINTMENT_BOOKED",
            variables={"appointment_id": str(created.appointment_id), "date": str(availability.available_date)},
        )
        return PublicBookAppointmentResponse(
            appointment_id=created.appointment_id,
            patient_id=created.patient_id,
            availability_id=created.availability_id,
            appointment_status=created.appointment_status.value,
            booking_source=created.booking_source.value,
        )

    def book_appointment(self, payload: PublicBookAppointmentRequest) -> PublicBookAppointmentResponse:
        return self._book_appointment_internal(
            availability_id=payload.availability_id,
            patient_input=payload.patient,
            booked_by_phone=payload.patient.phone.strip(),
        )

    def get_patient_for_booking(self, booking_session_token: str, patient_phone: str) -> PublicPatientProfileResponse:
        self._decode_valid_booking_session_phone(booking_session_token)
        patient = self.repo.get_patient_by_phone(patient_phone.strip())
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
        return PublicPatientProfileResponse(
            patient_id=patient.patient_id,
            full_name=patient.full_name,
            phone=patient.phone,
            gender=patient.gender,
            dob=patient.dob,
            blood_group=patient.blood_group,
            address=patient.address,
            emergency_contact=patient.emergency_contact,
        )

    def authenticated_book_appointment(self, payload: PublicAuthenticatedBookAppointmentRequest) -> PublicBookAppointmentResponse:
        actor_phone = self._decode_valid_booking_session_phone(payload.booking_session_token)
        patient_phone = payload.patient_phone.strip()
        patient = self.repo.get_patient_by_phone(patient_phone)
        if patient is not None:
            patient_payload = PublicBookingPatientInput(
                full_name=patient.full_name,
                phone=patient.phone,
                gender=patient.gender,
                dob=patient.dob,
                blood_group=patient.blood_group,
                address=patient.address,
                emergency_contact=patient.emergency_contact,
            )
            return self._book_appointment_internal(
                availability_id=payload.availability_id,
                patient_input=patient_payload,
                booked_by_phone=actor_phone,
            )
        if payload.patient is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient details are required for new patient booking.")
        if payload.patient.phone.strip() != patient_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient phone mismatch in booking payload.")
        return self._book_appointment_internal(
            availability_id=payload.availability_id,
            patient_input=payload.patient,
            booked_by_phone=actor_phone,
        )

    def list_booking_history(self, booking_session_token: str) -> list[PublicAppointmentHistoryItemResponse]:
        booked_by_phone = self._decode_valid_booking_session_phone(booking_session_token)
        rows = self.repo.list_appointment_rows_by_booked_phone(booked_by_phone=booked_by_phone)
        return [
            PublicAppointmentHistoryItemResponse(
                appointment_id=appointment.appointment_id,
                patient_id=patient.patient_id,
                patient_name=patient.full_name,
                patient_phone=patient.phone,
                doctor_user_id=availability.doctor_user_id,
                doctor_name=doctor.full_name,
                availability_id=availability.availability_id,
                available_date=availability.available_date,
                slot_start_time=slot.slot_start_time,
                slot_end_time=slot.slot_end_time,
                appointment_status=appointment.appointment_status.value,
                booking_source=appointment.booking_source.value if appointment.booking_source else None,
                cancellation_reason=appointment.cancellation_reason,
                completed_at=appointment.completed_at.isoformat() if appointment.completed_at else None,
                created_at=appointment.created_at.isoformat() if appointment.created_at else None,
                updated_at=appointment.updated_at.isoformat() if appointment.updated_at else None,
            )
            for appointment, patient, availability, slot, doctor in rows
        ]

    def cancel_appointment(self, appointment_id: int, payload: PublicAppointmentCancelRequest) -> PublicBookAppointmentResponse:
        now = self._now()
        booked_by_phone = self._decode_valid_booking_session_phone(payload.booking_session_token)
        next_waiting = None
        with self.db.begin_nested():
            appointment = self.repo.get_appointment_for_update_by_booked_phone(
                appointment_id=appointment_id,
                booked_by_phone=booked_by_phone,
            )
            if appointment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
            if appointment.appointment_status != AppointmentStatus.BOOKED:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only BOOKED appointments can be cancelled.")
            availability = self.repo.get_availability_for_booking(appointment.availability_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            appointment.appointment_status = AppointmentStatus.CANCELLED_BY_PATIENT
            appointment.cancellation_reason = payload.cancellation_reason.strip()
            appointment.updated_at = now
            self.repo.save_appointment(appointment)
            next_waiting = self.repo.get_next_waiting_entry_for_update(appointment.availability_id)
            if next_waiting is None:
                availability.slot_status = SlotStatus.AVAILABLE
            else:
                next_waiting.status = WaitingStatus.NOTIFIED
                next_waiting.notified_at = now
                next_waiting.expires_at = now + timedelta(minutes=15)
                next_waiting.updated_at = now
                self.repo.save_waiting_entry(next_waiting)
                availability.slot_status = SlotStatus.BLOCKED
            availability.updated_at = now
            self.repo.update_availability(availability)
        self.notification_service.create_for_user(
            user_id=availability.doctor_user_id,
            notification_type=NotificationType.APPOINTMENT_CANCELLED,
            title="Appointment cancelled by patient",
            message=f"Appointment #{appointment.appointment_id} was cancelled by patient.",
            metadata={"appointment_id": appointment.appointment_id},
        )
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK,),
            notification_type=NotificationType.APPOINTMENT_CANCELLED,
            title="Online appointment cancelled",
            message=f"Appointment #{appointment.appointment_id} was cancelled by patient.",
            metadata={"appointment_id": appointment.appointment_id},
        )
        self.communication_service.send_sms(
            phone=booked_by_phone,
            template_key="APPOINTMENT_CANCELLED",
            variables={"appointment_id": str(appointment.appointment_id), "reason": payload.cancellation_reason.strip()},
        )
        if next_waiting is not None:
            self.notification_service.create_for_roles(
                role_names=(ROLE_FRONTDESK,),
                notification_type=NotificationType.WAITING_LIST_AVAILABLE,
                title="Waiting list patient notified",
                message=f"Waiting entry #{next_waiting.waiting_id} has been notified for availability #{next_waiting.availability_id}.",
                metadata={"waiting_id": next_waiting.waiting_id, "availability_id": next_waiting.availability_id},
            )
            logger.info(
                "Waiting list entry notified waiting_id=%s availability_id=%s after cancellation appointment_id=%s",
                next_waiting.waiting_id,
                next_waiting.availability_id,
                appointment.appointment_id,
            )
        return PublicBookAppointmentResponse(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            availability_id=appointment.availability_id,
            appointment_status=appointment.appointment_status.value,
            booking_source=appointment.booking_source.value if appointment.booking_source else "",
        )

    def reschedule_appointment(self, appointment_id: int, payload: PublicAppointmentRescheduleRequest) -> PublicBookAppointmentResponse:
        now = self._now()
        booked_by_phone = self._decode_valid_booking_session_phone(payload.booking_session_token)
        effective_slot_ids = self._effective_slot_ids()
        next_waiting = None
        with self.db.begin_nested():
            appointment = self.repo.get_appointment_for_update_by_booked_phone(
                appointment_id=appointment_id,
                booked_by_phone=booked_by_phone,
            )
            if appointment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
            if appointment.appointment_status != AppointmentStatus.BOOKED:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only BOOKED appointments can be rescheduled.")
            old_availability = self.repo.get_availability_for_booking(appointment.availability_id)
            if old_availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current availability not found.")
            new_availability = self.repo.get_availability_for_booking(payload.new_availability_id)
            if new_availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New availability not found.")
            if new_availability.slot_id not in effective_slot_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected new slot is no longer valid for current clinic schedule.")
            if new_availability.slot_status != SlotStatus.AVAILABLE:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected new slot is not available.")
            existing_new_appointment = self.repo.get_appointment_by_availability_id(payload.new_availability_id)
            if existing_new_appointment is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment already exists for selected new availability.")
            clinic_settings = self.repo.get_clinic_settings()
            appointment_limit_per_day = clinic_settings.appointment_limit_per_day if clinic_settings else 2
            existing_count = self.repo.count_patient_appointments_on_date_excluding(
                patient_id=appointment.patient_id,
                target_date=new_availability.available_date,
                exclude_appointment_id=appointment.appointment_id,
            )
            if existing_count >= appointment_limit_per_day:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient daily appointment limit reached for selected date.")
            next_waiting = self.repo.get_next_waiting_entry_for_update(old_availability.availability_id)
            if next_waiting is None:
                old_availability.slot_status = SlotStatus.AVAILABLE
            else:
                next_waiting.status = WaitingStatus.NOTIFIED
                next_waiting.notified_at = now
                next_waiting.expires_at = now + timedelta(minutes=15)
                next_waiting.updated_at = now
                self.repo.save_waiting_entry(next_waiting)
                old_availability.slot_status = SlotStatus.BLOCKED
            old_availability.updated_at = now
            self.repo.update_availability(old_availability)
            appointment.availability_id = new_availability.availability_id
            appointment.updated_at = now
            appointment.cancellation_reason = None
            self.repo.save_appointment(appointment)
            new_availability.slot_status = SlotStatus.BOOKED
            new_availability.updated_at = now
            self.repo.update_availability(new_availability)
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK,),
            notification_type=NotificationType.APPOINTMENT_BOOKED,
            title="Online appointment rescheduled",
            message=f"Appointment #{appointment.appointment_id} was rescheduled by patient.",
            metadata={"appointment_id": appointment.appointment_id, "old_availability_id": old_availability.availability_id, "new_availability_id": new_availability.availability_id},
        )
        self.notification_service.create_for_user(
            user_id=new_availability.doctor_user_id,
            notification_type=NotificationType.APPOINTMENT_BOOKED,
            title="Appointment rescheduled",
            message=f"Appointment #{appointment.appointment_id} was rescheduled to your slot.",
            metadata={"appointment_id": appointment.appointment_id},
        )
        self.communication_service.send_sms(
            phone=booked_by_phone,
            template_key="APPOINTMENT_RESCHEDULED",
            variables={"appointment_id": str(appointment.appointment_id), "new_date": str(new_availability.available_date)},
        )
        if next_waiting is not None:
            self.notification_service.create_for_roles(
                role_names=(ROLE_FRONTDESK,),
                notification_type=NotificationType.WAITING_LIST_AVAILABLE,
                title="Waiting list patient notified",
                message=f"Waiting entry #{next_waiting.waiting_id} has been notified for availability #{next_waiting.availability_id}.",
                metadata={"waiting_id": next_waiting.waiting_id, "availability_id": next_waiting.availability_id},
            )
            logger.info(
                "Waiting list entry notified waiting_id=%s availability_id=%s after reschedule appointment_id=%s",
                next_waiting.waiting_id,
                next_waiting.availability_id,
                appointment.appointment_id,
            )
        return PublicBookAppointmentResponse(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            availability_id=appointment.availability_id,
            appointment_status=appointment.appointment_status.value,
            booking_source=appointment.booking_source.value if appointment.booking_source else "",
        )

    def join_waiting_list(self, payload: PublicJoinWaitingListRequest) -> PublicJoinWaitingListResponse:
        now = self._now()
        patient_input = payload.patient
        effective_slot_ids = self._effective_slot_ids()
        with self.db.begin_nested():
            availability = self.repo.get_availability_for_booking(payload.availability_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            if availability.slot_id not in effective_slot_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected slot is no longer valid for current clinic schedule.")
            if availability.slot_status == SlotStatus.AVAILABLE:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is currently available. Please book directly.")
            patient = self.repo.get_patient_by_phone(patient_input.phone.strip())
            if patient is None:
                patient = self.repo.create_patient(
                    full_name=patient_input.full_name.strip(),
                    phone=patient_input.phone.strip(),
                    gender=patient_input.gender,
                    dob=patient_input.dob,
                    blood_group=patient_input.blood_group,
                    address=patient_input.address,
                    emergency_contact=patient_input.emergency_contact,
                    now=now,
                )
            existing_appointment = self.repo.get_appointment_by_availability_id(availability.availability_id)
            if (
                existing_appointment is not None
                and existing_appointment.appointment_status == AppointmentStatus.BOOKED
                and existing_appointment.patient_id == patient.patient_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Booked patient cannot join waiting list for the same slot.",
                )
            existing = self.repo.get_waiting_entry(patient_id=patient.patient_id, availability_id=availability.availability_id)
            if existing is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient is already in waiting list for this slot.")
            position = self.repo.get_next_waiting_position(availability.availability_id)
            entry = WaitingList(
                patient_id=patient.patient_id,
                availability_id=availability.availability_id,
                position=position,
                status=WaitingStatus.WAITING,
                created_at=now,
                updated_at=now,
            )
            try:
                created = self.repo.create_waiting_entry(entry)
            except IntegrityError as exc:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not join waiting list due to position conflict. Please retry.") from exc
        logger.info("Waiting list joined waiting_id=%s patient_id=%s availability_id=%s position=%s", created.waiting_id, created.patient_id, created.availability_id, created.position)
        return PublicJoinWaitingListResponse(
            waiting_id=created.waiting_id,
            patient_id=created.patient_id,
            availability_id=created.availability_id,
            position=created.position,
            status=created.status.value,
        )
