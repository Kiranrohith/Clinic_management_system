import logging
from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import WalkInToken
from app.models.enums import WalkInStatus
from app.repositories.frontdesk.walkin_repository import FrontdeskWalkInRepository
from app.schemas.frontdesk.walkin import (
    FrontdeskWalkInCreateRequest,
    FrontdeskWalkInListItemResponse,
    FrontdeskWalkInResponse,
    FrontdeskWalkInStatusUpdateRequest,
)

logger = logging.getLogger("clinic.frontdesk")


class FrontdeskWalkInService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FrontdeskWalkInRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def create_walkin_token(
        self,
        payload: FrontdeskWalkInCreateRequest,
        actor_user_id: int,
    ) -> FrontdeskWalkInResponse:
        now = self._now()
        patient = self.repo.get_patient_by_phone(payload.patient_phone.strip())
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
        if self.repo.get_doctor(payload.doctor_user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

        next_number = self.repo.get_next_walkin_token_number(
            doctor_user_id=payload.doctor_user_id,
            token_date=payload.token_date,
        )
        token = WalkInToken(
            token_number=next_number,
            token_date=payload.token_date,
            patient_id=patient.patient_id,
            doctor_user_id=payload.doctor_user_id,
            status=WalkInStatus.WAITING,
            notes=payload.notes,
            created_by=actor_user_id,
            updated_by=actor_user_id,
            created_at=now,
            updated_at=now,
        )
        try:
            created = self.repo.create_walkin_token(token)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create walk-in token due to conflict.") from exc

        logger.info("Frontdesk created walk-in token token_id=%s doctor_user_id=%s number=%s", created.token_id, created.doctor_user_id, created.token_number)
        return FrontdeskWalkInResponse(
            token_id=created.token_id,
            token_number=created.token_number,
            token_date=created.token_date,
            patient_id=created.patient_id,
            doctor_user_id=created.doctor_user_id,
            status=created.status,
            notes=created.notes,
        )

    def list_walkin_token_history(
        self,
        token_date: date | None,
        doctor_user_id: int | None,
    ) -> list[FrontdeskWalkInListItemResponse]:
        rows = self.repo.list_walkin_token_rows(doctor_user_id=doctor_user_id, token_date=token_date)
        return [
            FrontdeskWalkInListItemResponse(
                token_id=token.token_id,
                token_number=token.token_number,
                token_date=token.token_date,
                patient_id=patient.patient_id,
                patient_name=patient.full_name,
                patient_phone=patient.phone,
                doctor_user_id=token.doctor_user_id,
                doctor_name=doctor_user.full_name,
                status=token.status,
                notes=token.notes,
                created_at=token.created_at,
                updated_at=token.updated_at,
            )
            for token, patient, doctor_user in rows
        ]

    def get_walkin_token(self, token_id: int) -> FrontdeskWalkInListItemResponse:
        row = self.repo.get_walkin_token_row(token_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Walk-in token not found.")
        token, patient, doctor_user = row
        return FrontdeskWalkInListItemResponse(
            token_id=token.token_id,
            token_number=token.token_number,
            token_date=token.token_date,
            patient_id=patient.patient_id,
            patient_name=patient.full_name,
            patient_phone=patient.phone,
            doctor_user_id=token.doctor_user_id,
            doctor_name=doctor_user.full_name,
            status=token.status,
            notes=token.notes,
            created_at=token.created_at,
            updated_at=token.updated_at,
        )

    def update_walkin_status(
        self,
        token_id: int,
        payload: FrontdeskWalkInStatusUpdateRequest,
        actor_user_id: int,
    ) -> FrontdeskWalkInListItemResponse:
        now = self._now()
        with self.db.begin_nested():
            token = self.repo.get_walkin_token_for_update(token_id)
            if token is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Walk-in token not found.")
            token.status = payload.status
            token.notes = payload.notes.strip() if payload.notes else token.notes
            token.updated_by = actor_user_id
            token.updated_at = now
            self.repo.save_walkin_token(token)
        return self.get_walkin_token(token_id)
