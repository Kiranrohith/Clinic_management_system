from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import User


class PublicPrescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_prescription_rows_by_phone(
        self,
        phone: str,
    ) -> list[tuple[Prescription, User]]:
        stmt = (
            select(Prescription, User)
            .join(Patient, Patient.patient_id == Prescription.patient_id)
            .join(User, User.user_id == Prescription.doctor_user_id)
            .where(Patient.phone == phone)
            .order_by(Prescription.created_at.desc(), Prescription.prescription_id.desc())
        )
        return list(self.db.execute(stmt).all())
