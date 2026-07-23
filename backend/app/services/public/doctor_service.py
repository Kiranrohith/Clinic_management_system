import logging
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.public.doctor_repository import PublicDoctorRepository
from app.schemas.public.doctor import PublicDoctorResponse, PublicSpecializationResponse, PublicAvailabilityResponse
from app.services.admin.slot_service import AdminSlotService

logger = logging.getLogger("clinic.public")


class PublicDoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PublicDoctorRepository(db)

    def list_specializations(self) -> list[PublicSpecializationResponse]:
        rows = self.repo.list_specializations()
        return [
            PublicSpecializationResponse(
                specialization_id=item.specialization_id,
                specialization_name=item.specialization_name,
            )
            for item in rows
        ]

    def list_doctors(self, specialization_id: int | None) -> list[PublicDoctorResponse]:
        rows = self.repo.list_doctor_rows(specialization_id=specialization_id)
        doctors_map: dict[int, PublicDoctorResponse] = {}
        for doctor, user, row_specialization_id, row_specialization_name in rows:
            existing = doctors_map.get(doctor.doctor_user_id)
            if existing is None:
                existing = PublicDoctorResponse(
                    doctor_user_id=doctor.doctor_user_id,
                    full_name=user.full_name,
                    qualification=doctor.qualification,
                    experience_years=doctor.experience_years,
                    consultation_fee=float(doctor.consultation_fee) if doctor.consultation_fee is not None else None,
                    about=doctor.about,
                    specialization_ids=[],
                    specialization_names=[],
                )
                doctors_map[doctor.doctor_user_id] = existing
            if row_specialization_id is not None and row_specialization_name is not None:
                if row_specialization_id not in existing.specialization_ids:
                    existing.specialization_ids.append(row_specialization_id)
                    existing.specialization_names.append(row_specialization_name)
        return list(doctors_map.values())

    def get_doctor(self, doctor_user_id: int) -> PublicDoctorResponse:
        doctors = self.list_doctors(specialization_id=None)
        for doctor in doctors:
            if doctor.doctor_user_id == doctor_user_id:
                return doctor
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    def _effective_slot_ids(self) -> set[int]:
        return {slot.slot_id for slot in AdminSlotService(self.db).list_slots()}

    def list_availabilities(
        self,
        doctor_user_id: int | None,
        available_date: date | None,
    ) -> list[PublicAvailabilityResponse]:
        effective_slot_ids = self._effective_slot_ids()
        rows = self.repo.list_available_rows(doctor_user_id=doctor_user_id, available_date=available_date)
        return [
            PublicAvailabilityResponse(
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
