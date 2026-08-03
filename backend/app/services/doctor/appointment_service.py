import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN, ROLE_FRONTDESK
from app.models.enums import AppointmentStatus, NotificationType, SlotStatus, WaitingStatus
from app.repositories.doctor.appointment_repository import DoctorAppointmentRepository
from app.repositories.doctor.availability_repository import DoctorAvailabilityRepository
from app.repositories.doctor.prescription_repository import DoctorPrescriptionRepository
from app.services.notification_service import NotificationService
from app.schemas.doctor.appointment import (
    DoctorAppointmentResponse,
    DoctorAppointmentDetailResponse,
    DoctorCancelAppointmentRequest,
    DoctorPatientSummaryResponse,
)
from app.schemas.doctor.prescription import DoctorPrescriptionHistoryItemResponse, DoctorPrescriptionResponse

logger = logging.getLogger("clinic.doctor")


class DoctorAppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.appt_repo = DoctorAppointmentRepository(db)
        self.avail_repo = DoctorAvailabilityRepository(db)
        self.rx_repo = DoctorPrescriptionRepository(db)
        self.notification_service = NotificationService(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _today() -> date:
        return date.today()

    @staticmethod
    def _calculate_age(dob: date | None) -> int | None:
        if dob is None:
            return None
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def _parse_appointment_status(value: str | None) -> AppointmentStatus | None:
        if value is None:
            return None
        try:
            return AppointmentStatus(value)
        except ValueError as exc:
            raise ValueError("Invalid appointment_status filter.") from exc

    def list_appointments(
        self,
        doctor_user_id: int,
        available_date: date | None,
        appointment_status: str | None,
    ) -> list[dict[str, Any]]:
        parsed_status = self._parse_appointment_status(appointment_status)
        rows = self.appt_repo.list_appointment_rows(
            doctor_user_id=doctor_user_id,
            available_date=available_date,
            appointment_status=parsed_status,
        )
        return [
            DoctorAppointmentResponse(
                appointment_id=a.appointment_id,
                patient_id=patient.patient_id,
                patient_name=patient.full_name,
                patient_phone=patient.phone,
                available_date=availability.available_date,
                slot_start_time=slot.slot_start_time,
                slot_end_time=slot.slot_end_time,
                appointment_status=a.appointment_status,
                booking_source=a.booking_source.value if a.booking_source else None,
                cancellation_reason=a.cancellation_reason,
                completed_at=a.completed_at,
            ).model_dump()
            for a, availability, slot, patient in rows
        ]

    def get_appointment_detail(self, doctor_user_id: int, appointment_id: int) -> DoctorAppointmentDetailResponse:
        row = self.appt_repo.get_appointment_row(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
        if row is None:
            raise LookupError("Appointment not found.")
        appointment, availability, slot, patient = row
        current_prescription = self.rx_repo.get_prescription_by_appointment(
            doctor_user_id=doctor_user_id, appointment_id=appointment_id
        )
        history_rows = self.rx_repo.list_prescription_history_rows(
            patient_id=patient.patient_id, exclude_appointment_id=appointment_id
        )
        return DoctorAppointmentDetailResponse(
            appointment_id=appointment.appointment_id,
            patient=DoctorPatientSummaryResponse(
                patient_id=patient.patient_id,
                full_name=patient.full_name,
                phone=patient.phone,
                gender=patient.gender,
                dob=patient.dob,
                age=self._calculate_age(patient.dob),
                blood_group=patient.blood_group,
                address=patient.address,
                emergency_contact=patient.emergency_contact,
            ),
            available_date=availability.available_date,
            slot_start_time=slot.slot_start_time,
            slot_end_time=slot.slot_end_time,
            appointment_status=appointment.appointment_status,
            booking_source=appointment.booking_source.value if appointment.booking_source else None,
            cancellation_reason=appointment.cancellation_reason,
            completed_at=appointment.completed_at,
            reason_for_visit=None,
            can_edit_prescription=(
                availability.available_date == self._today()
                and appointment.appointment_status in [AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED]
            ),
            current_prescription=self._to_rx_response(current_prescription) if current_prescription else None,
            previous_prescriptions=[
                DoctorPrescriptionHistoryItemResponse(
                    prescription_id=rx.prescription_id,
                    appointment_id=rx.appointment_id,
                    appointment_date=h_avail.available_date,
                    slot_start_time=h_slot.slot_start_time,
                    slot_end_time=h_slot.slot_end_time,
                    doctor_user_id=doctor_user.user_id,
                    doctor_name=doctor_user.full_name,
                    diagnosis=rx.diagnosis,
                    medicines=rx.medicines,
                    dosage=rx.dosage,
                    frequency=rx.frequency,
                    duration=rx.duration,
                    doctor_advice=rx.doctor_advice,
                    internal_notes=rx.internal_notes,
                    follow_up_date=rx.follow_up_date,
                )
                for rx, _, h_avail, h_slot, doctor_user in history_rows
            ],
        )

    def complete_appointment(self, doctor_user_id: int, appointment_id: int) -> dict[str, Any]:
        now = self._now()
        with self.db.begin_nested():
            appointment = self.appt_repo.get_appointment_for_update(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
            if appointment is None:
                raise LookupError("Appointment not found.")
            if appointment.appointment_status != AppointmentStatus.BOOKED:
                raise ValueError("Only BOOKED appointments can be completed.")
            appointment.appointment_status = AppointmentStatus.COMPLETED
            appointment.completed_at = now
            appointment.updated_by = doctor_user_id
            appointment.updated_at = now
            self.appt_repo.save_appointment(appointment)
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK, ROLE_ADMIN),
            notification_type=NotificationType.APPOINTMENT_COMPLETED,
            title="Appointment completed",
            message=f"Appointment #{appointment_id} marked as completed by doctor.",
            metadata={"appointment_id": appointment_id},
        )
        return self._get_appointment_response(doctor_user_id, appointment_id)

    def cancel_appointment(
        self,
        doctor_user_id: int,
        appointment_id: int,
        payload: DoctorCancelAppointmentRequest,
    ) -> dict[str, Any]:
        now = self._now()
        with self.db.begin_nested():
            appointment = self.appt_repo.get_appointment_for_update(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
            if appointment is None:
                raise LookupError("Appointment not found.")
            if appointment.appointment_status != AppointmentStatus.BOOKED:
                raise ValueError("Only BOOKED appointments can be cancelled by doctor.")
            availability = self.avail_repo.get_availability_for_update(availability_id=appointment.availability_id, doctor_user_id=doctor_user_id)
            if availability is None:
                raise LookupError("Availability not found.")
            appointment.appointment_status = AppointmentStatus.CANCELLED_BY_DOCTOR
            appointment.cancellation_reason = payload.cancellation_reason.strip()
            appointment.updated_by = doctor_user_id
            appointment.updated_at = now
            self.appt_repo.save_appointment(appointment)
            waiting_entries = self.appt_repo.list_waiting_entries_for_update(availability.availability_id)
            if not waiting_entries:
                availability.slot_status = SlotStatus.AVAILABLE
            else:
                first_waiting = sorted(waiting_entries, key=lambda item: item.position)[0]
                first_waiting.status = WaitingStatus.NOTIFIED
                first_waiting.notified_at = now
                first_waiting.expires_at = now + timedelta(minutes=15)
                first_waiting.updated_at = now
                self.appt_repo.save_waiting_entry(first_waiting)
                availability.slot_status = SlotStatus.BLOCKED
            availability.updated_by = doctor_user_id
            availability.updated_at = now
            self.avail_repo.save_availability(availability)
        self.notification_service.create_for_roles(
            role_names=(ROLE_FRONTDESK, ROLE_ADMIN),
            notification_type=NotificationType.APPOINTMENT_CANCELLED,
            title="Appointment cancelled by doctor",
            message=f"Appointment #{appointment_id} was cancelled by doctor.",
            metadata={"appointment_id": appointment_id},
        )
        if waiting_entries:
            self.notification_service.create_for_roles(
                role_names=(ROLE_FRONTDESK,),
                notification_type=NotificationType.WAITING_LIST_AVAILABLE,
                title="Waiting list patient notified",
                message=f"Waiting list patient notified for availability #{availability.availability_id}.",
                metadata={"availability_id": availability.availability_id},
            )
        return self._get_appointment_response(doctor_user_id, appointment_id)

    def _get_appointment_response(self, doctor_user_id: int, appointment_id: int) -> dict[str, Any]:
        rows = self.appt_repo.list_appointment_rows(doctor_user_id=doctor_user_id, available_date=None, appointment_status=None)
        for appointment, availability, slot, patient in rows:
            if appointment.appointment_id == appointment_id:
                return DoctorAppointmentResponse(
                    appointment_id=appointment.appointment_id,
                    patient_id=patient.patient_id,
                    patient_name=patient.full_name,
                    patient_phone=patient.phone,
                    available_date=availability.available_date,
                    slot_start_time=slot.slot_start_time,
                    slot_end_time=slot.slot_end_time,
                    appointment_status=appointment.appointment_status,
                    booking_source=appointment.booking_source.value if appointment.booking_source else None,
                    cancellation_reason=appointment.cancellation_reason,
                    completed_at=appointment.completed_at,
                ).model_dump()
        raise LookupError("Appointment not found.")

    @staticmethod
    def _to_rx_response(prescription) -> DoctorPrescriptionResponse:
        return DoctorPrescriptionResponse(
            prescription_id=prescription.prescription_id,
            appointment_id=prescription.appointment_id,
            patient_id=prescription.patient_id,
            doctor_user_id=prescription.doctor_user_id,
            diagnosis=prescription.diagnosis,
            medicines=prescription.medicines,
            dosage=prescription.dosage,
            frequency=prescription.frequency,
            duration=prescription.duration,
            doctor_advice=prescription.doctor_advice,
            internal_notes=prescription.internal_notes,
            follow_up_date=prescription.follow_up_date,
            follow_up_reminder_sent=prescription.follow_up_reminder_sent,
        )
