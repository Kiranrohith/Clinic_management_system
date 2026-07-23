import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.frontdesk.patient_repository import FrontdeskPatientRepository
from app.schemas.frontdesk.patient import (
    FrontdeskPatientUpsertRequest,
    FrontdeskPatientResponse,
    FrontdeskPatientSearchItemResponse,
)

logger = logging.getLogger("clinic.frontdesk")


class FrontdeskPatientService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FrontdeskPatientRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def upsert_patient(self, payload: FrontdeskPatientUpsertRequest) -> FrontdeskPatientResponse:
        now = self._now()
        phone = payload.phone.strip()
        patient = self.repo.get_patient_by_phone(phone)
        if patient is None:
            patient = Patient(
                full_name=payload.full_name.strip(),
                phone=phone,
                gender=payload.gender,
                dob=payload.dob,
                blood_group=payload.blood_group,
                address=payload.address,
                emergency_contact=payload.emergency_contact,
                created_at=now,
                updated_at=now,
            )
            saved = self.repo.create_patient(patient)
            logger.info("Frontdesk created patient patient_id=%s phone=%s", saved.patient_id, saved.phone)
        else:
            patient.full_name = payload.full_name.strip()
            patient.gender = payload.gender
            patient.dob = payload.dob
            patient.blood_group = payload.blood_group
            patient.address = payload.address
            patient.emergency_contact = payload.emergency_contact
            patient.updated_at = now
            saved = self.repo.update_patient(patient)
            logger.info("Frontdesk updated patient patient_id=%s", saved.patient_id)
        return self._to_response(saved)

    def get_patient_by_phone(self, phone: str) -> FrontdeskPatientResponse:
        patient = self.repo.get_patient_by_phone(phone.strip())
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
        return self._to_response(patient)

    def search_patients(self, query: str, limit: int) -> list[FrontdeskPatientSearchItemResponse]:
        search = query.strip()
        if len(search) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search query must be at least 2 characters.")
        safe_limit = max(1, min(limit, 20))
        rows = self.repo.search_patients(search, safe_limit)
        return [FrontdeskPatientSearchItemResponse(patient_id=p.patient_id, full_name=p.full_name, phone=p.phone) for p in rows]

    @staticmethod
    def _to_response(patient: Patient) -> FrontdeskPatientResponse:
        return FrontdeskPatientResponse(
            patient_id=patient.patient_id,
            full_name=patient.full_name,
            phone=patient.phone,
            gender=patient.gender,
            dob=patient.dob,
            blood_group=patient.blood_group,
            address=patient.address,
            emergency_contact=patient.emergency_contact,
        )
