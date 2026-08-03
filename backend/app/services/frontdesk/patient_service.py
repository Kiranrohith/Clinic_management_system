import logging
from datetime import UTC, datetime
from typing import Any

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

    def upsert_patient(self, payload: FrontdeskPatientUpsertRequest) -> dict[str, Any]:
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
            message = "Patient created successfully."
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
            message = "Patient updated successfully."
        return {
            "status_code": 200,
            "message": message,
            "data": self._to_response(saved).model_dump(),
        }

    def get_patient_by_phone(self, phone: str) -> dict[str, Any]:
        patient = self.repo.get_patient_by_phone(phone.strip())
        if patient is None:
            return {"status_code": 404, "message": "Patient not found.", "data": None}
        return {
            "status_code": 200,
            "message": "Patient fetched successfully.",
            "data": self._to_response(patient).model_dump(),
        }

    def search_patients(self, query: str, limit: int) -> dict[str, Any]:
        search = query.strip()
        if len(search) < 2:
            return {"status_code": 400, "message": "Search query must be at least 2 characters.", "data": []}
        safe_limit = max(1, min(limit, 20))
        rows = self.repo.search_patients(search, safe_limit)
        return {
            "status_code": 200,
            "message": "Patients fetched successfully.",
            "data": [
                FrontdeskPatientSearchItemResponse(patient_id=p.patient_id, full_name=p.full_name, phone=p.phone).model_dump()
                for p in rows
            ],
        }

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
