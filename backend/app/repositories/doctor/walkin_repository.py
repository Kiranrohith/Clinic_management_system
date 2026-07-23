from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import WalkInToken
from app.models.patient import Patient


class DoctorWalkInRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_walkin_rows(
        self,
        doctor_user_id: int,
        token_date: date | None,
    ) -> list[tuple[WalkInToken, Patient]]:
        stmt = (
            select(WalkInToken, Patient)
            .join(Patient, Patient.patient_id == WalkInToken.patient_id)
            .where(WalkInToken.doctor_user_id == doctor_user_id)
            .order_by(WalkInToken.token_date.desc(), WalkInToken.token_number.asc())
        )
        if token_date is not None:
            stmt = stmt.where(WalkInToken.token_date == token_date)
        return list(self.db.execute(stmt).all())

    def get_walkin_for_update(
        self,
        doctor_user_id: int,
        token_id: int,
    ) -> WalkInToken | None:
        stmt = (
            select(WalkInToken)
            .where(
                WalkInToken.doctor_user_id == doctor_user_id,
                WalkInToken.token_id == token_id,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_walkin(self, walkin: WalkInToken) -> WalkInToken:
        self.db.add(walkin)
        self.db.flush()
        return walkin
