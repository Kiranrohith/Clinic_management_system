import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import WalkInStatus
from app.repositories.doctor.walkin_repository import DoctorWalkInRepository
from app.schemas.doctor.walkin import DoctorWalkInResponse, DoctorWalkInStatusUpdateRequest

logger = logging.getLogger("clinic.doctor")


class DoctorWalkInService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DoctorWalkInRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def list_walkin_tokens(self, doctor_user_id: int, token_date) -> list[DoctorWalkInResponse]:
        rows = self.repo.list_walkin_rows(doctor_user_id=doctor_user_id, token_date=token_date)
        return [
            DoctorWalkInResponse(
                token_id=w.token_id,
                token_number=w.token_number,
                token_date=w.token_date,
                patient_id=patient.patient_id,
                patient_name=patient.full_name,
                patient_phone=patient.phone,
                status=w.status,
                notes=w.notes,
            )
            for w, patient in rows
        ]

    def update_walkin_status(
        self,
        doctor_user_id: int,
        token_id: int,
        payload: DoctorWalkInStatusUpdateRequest,
    ) -> DoctorWalkInResponse:
        with self.db.begin_nested():
            walkin = self.repo.get_walkin_for_update(doctor_user_id=doctor_user_id, token_id=token_id)
            if walkin is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Walk-in token not found.")
            if walkin.status == WalkInStatus.CANCELLED and payload.status != WalkInStatus.CANCELLED:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cancelled walk-in token status cannot be changed.")
            walkin.status = payload.status
            walkin.notes = payload.notes if payload.notes is not None else walkin.notes
            walkin.updated_by = doctor_user_id
            walkin.updated_at = self._now()
            saved = self.repo.save_walkin(walkin)
        rows = self.repo.list_walkin_rows(doctor_user_id=doctor_user_id, token_date=saved.token_date)
        for row in rows:
            token, patient = row
            if token.token_id == saved.token_id:
                return DoctorWalkInResponse(
                    token_id=token.token_id,
                    token_number=token.token_number,
                    token_date=token.token_date,
                    patient_id=patient.patient_id,
                    patient_name=patient.full_name,
                    patient_phone=patient.phone,
                    status=token.status,
                    notes=token.notes,
                )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Walk-in token not found.")
