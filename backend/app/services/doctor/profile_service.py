import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.doctor.profile_repository import DoctorProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.doctor.profile import DoctorProfileResponse, DoctorProfileUpdateRequest

logger = logging.getLogger("clinic.doctor")


class DoctorProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DoctorProfileRepository(db)
        self.user_repository = UserRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def get_profile(self, doctor_user_id: int) -> DoctorProfileResponse:
        profile_row = self.repo.get_doctor_profile_row(doctor_user_id)
        if profile_row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")
        user, doctor = profile_row
        return DoctorProfileResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role_name=user.role.role_name,
            status=user.status,
            qualification=doctor.qualification,
            experience_years=doctor.experience_years,
            about=doctor.about,
            specialization_names=self.repo.list_doctor_specialization_names(doctor_user_id),
        )

    def update_profile(self, doctor_user_id: int, payload: DoctorProfileUpdateRequest) -> DoctorProfileResponse:
        user = self.user_repository.get_by_id(doctor_user_id)
        doctor = self.repo.get_doctor_for_update(doctor_user_id)
        if user is None or user.role is None or doctor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")
        normalized_phone = payload.phone.strip() if payload.phone else None
        if normalized_phone:
            existing_phone_user = self.user_repository.get_by_phone(normalized_phone)
            if existing_phone_user is not None and existing_phone_user.user_id != doctor_user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already belongs to another user.")
        now = self._now()
        user.full_name = payload.full_name.strip()
        user.phone = normalized_phone
        user.updated_by = doctor_user_id
        user.updated_at = now
        self.user_repository.save(user)
        doctor.qualification = payload.qualification.strip() if payload.qualification else None
        doctor.experience_years = payload.experience_years
        doctor.about = payload.about.strip() if payload.about else None
        doctor.updated_by = doctor_user_id
        doctor.updated_at = now
        self.repo.save_doctor(doctor)
        return self.get_profile(doctor_user_id)
