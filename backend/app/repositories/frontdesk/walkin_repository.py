from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models.appointment import WalkInToken
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User


class FrontdeskWalkInRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_patient_by_phone(self, phone: str) -> Patient | None:
        stmt = select(Patient).where(Patient.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_patient_by_phone(self, phone:str)-> Patient|None:
        stmt=select(Patient).where(Patient.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_doctor(self, doctor_user_id: int) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.doctor_user_id == doctor_user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_next_walkin_token_number(self, doctor_user_id: int, token_date: date) -> int:
        stmt = select(func.max(WalkInToken.token_number)).where(
            WalkInToken.doctor_user_id == doctor_user_id,
            WalkInToken.token_date == token_date,
        )
        max_token = self.db.scalar(stmt)
        return int(max_token or 0) + 1

    def create_walkin_token(self, token: WalkInToken) -> WalkInToken:
        self.db.add(token)
        self.db.flush()
        return token

    def list_walkin_token_rows(
        self,
        doctor_user_id: int | None,
        token_date: date | None,
    ) -> list[tuple[WalkInToken, Patient, User]]:
        doctor_user = aliased(User)
        stmt = (
            select(WalkInToken, Patient, doctor_user)
            .join(Patient, Patient.patient_id == WalkInToken.patient_id)
            .join(doctor_user, doctor_user.user_id == WalkInToken.doctor_user_id)
            .order_by(WalkInToken.token_date.desc(), WalkInToken.token_number.asc(), WalkInToken.token_id.asc())
        )
        if token_date is not None:
            stmt = stmt.where(WalkInToken.token_date == token_date)
        if doctor_user_id is not None:
            stmt = stmt.where(WalkInToken.doctor_user_id == doctor_user_id)
        return list(self.db.execute(stmt).all())

    def get_walkin_token_row(self, token_id: int) -> tuple[WalkInToken, Patient, User] | None:
        doctor_user = aliased(User)
        stmt = (
            select(WalkInToken, Patient, doctor_user)
            .join(Patient, Patient.patient_id == WalkInToken.patient_id)
            .join(doctor_user, doctor_user.user_id == WalkInToken.doctor_user_id)
            .where(WalkInToken.token_id == token_id)
        )
        return self.db.execute(stmt).one_or_none()

    def get_walkin_token_for_update(self, token_id: int) -> WalkInToken | None:
        stmt = select(WalkInToken).where(WalkInToken.token_id == token_id).with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def save_walkin_token(self, token: WalkInToken) -> WalkInToken:
        self.db.add(token)
        self.db.flush()
        return token
