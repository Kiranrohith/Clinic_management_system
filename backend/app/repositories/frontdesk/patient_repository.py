from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class FrontdeskPatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_patient_by_phone(self, phone: str) -> Patient | None:
        stmt = select(Patient).where(Patient.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def search_patients(self, query: str, limit: int) -> list[Patient]:
        like_value = f"%{query}%"
        stmt = (
            select(Patient)
            .where(
                or_(
                    Patient.full_name.ilike(like_value),
                    Patient.phone.ilike(like_value),
                )
            )
            .order_by(Patient.full_name.asc(), Patient.patient_id.asc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create_patient(self, patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.flush()
        return patient

    def update_patient(self, patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.flush()
        return patient
