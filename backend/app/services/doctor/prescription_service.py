import logging
from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN, ROLE_FRONTDESK
from app.models.enums import AppointmentStatus, NotificationType
from app.models.prescription import Prescription
from app.repositories.doctor.appointment_repository import DoctorAppointmentRepository
from app.repositories.doctor.availability_repository import DoctorAvailabilityRepository
from app.repositories.doctor.prescription_repository import DoctorPrescriptionRepository
from app.services.notification_service import NotificationService
from app.schemas.doctor.prescription import (
    DoctorPrescriptionUpsertRequest,
    DoctorPrescriptionResponse,
)

logger = logging.getLogger("clinic.doctor")


class DoctorPrescriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.rx_repo = DoctorPrescriptionRepository(db)
        self.appt_repo = DoctorAppointmentRepository(db)
        self.avail_repo = DoctorAvailabilityRepository(db)
        self.notification_service = NotificationService(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _today() -> date:
        return date.today()

    def upsert_prescription(
        self,
        doctor_user_id: int,
        appointment_id: int,
        payload: DoctorPrescriptionUpsertRequest,
    ) -> DoctorPrescriptionResponse:
        now = self._now()
        with self.db.begin_nested():
            appointment = self.appt_repo.get_appointment_for_update(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
            if appointment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
            if appointment.appointment_status not in [AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED]:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescription can only be managed for BOOKED or COMPLETED appointments.")
            availability = self.avail_repo.get_availability_for_update(availability_id=appointment.availability_id, doctor_user_id=doctor_user_id)
            if availability is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found.")
            if availability.available_date != self._today():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescriptions can only be edited on the appointment date.")
            existing = self.rx_repo.get_prescription_by_appointment(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
            if existing is None:
                prescription = Prescription(
                    appointment_id=appointment.appointment_id,
                    patient_id=appointment.patient_id,
                    doctor_user_id=doctor_user_id,
                    diagnosis=payload.diagnosis,
                    medicines=payload.medicines,
                    dosage=payload.dosage,
                    frequency=payload.frequency,
                    duration=payload.duration,
                    doctor_advice=payload.doctor_advice,
                    internal_notes=payload.internal_notes,
                    follow_up_date=payload.follow_up_date,
                    follow_up_reminder_sent=False,
                    created_by=doctor_user_id,
                    updated_by=doctor_user_id,
                    created_at=now,
                    updated_at=now,
                )
                saved = self.rx_repo.create_prescription(prescription)
            else:
                existing.diagnosis = payload.diagnosis
                existing.medicines = payload.medicines
                existing.dosage = payload.dosage
                existing.frequency = payload.frequency
                existing.duration = payload.duration
                existing.doctor_advice = payload.doctor_advice
                existing.internal_notes = payload.internal_notes
                existing.follow_up_date = payload.follow_up_date
                existing.updated_by = doctor_user_id
                existing.updated_at = now
                saved = self.rx_repo.save_prescription(existing)
        logger.info("Doctor upserted prescription appointment_id=%s doctor_user_id=%s", appointment_id, doctor_user_id)
        if saved.follow_up_date is not None:
            self.notification_service.create_for_roles(
                role_names=(ROLE_FRONTDESK, ROLE_ADMIN),
                notification_type=NotificationType.FOLLOW_UP_REMINDER,
                title="Follow-up date recorded",
                message=f"Follow-up date {saved.follow_up_date} was recorded for appointment #{appointment_id}.",
                metadata={"appointment_id": appointment_id, "follow_up_date": str(saved.follow_up_date)},
            )
        return self._to_response(saved)

    def get_prescription(self, doctor_user_id: int, appointment_id: int) -> DoctorPrescriptionResponse:
        prescription = self.rx_repo.get_prescription_by_appointment(doctor_user_id=doctor_user_id, appointment_id=appointment_id)
        if prescription is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found.")
        return self._to_response(prescription)

    @staticmethod
    def _to_response(prescription: Prescription) -> DoctorPrescriptionResponse:
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
