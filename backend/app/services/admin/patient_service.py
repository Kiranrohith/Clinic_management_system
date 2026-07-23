from sqlalchemy.orm import Session

from app.repositories.admin.patient_repository import AdminPatientRepository
from app.schemas.admin.patient import PatientListItemResponse


class AdminPatientService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminPatientRepository(db)

    def list_patients(self) -> list[PatientListItemResponse]:
        rows = self.repo.list_patients_with_appointment_counts()
        return [
            PatientListItemResponse(
                patient_id=patient.patient_id,
                full_name=patient.full_name,
                phone=patient.phone,
                gender=patient.gender.value if patient.gender else None,
                dob=patient.dob,
                blood_group=patient.blood_group,
                appointment_count=appointment_count,
                created_at=patient.created_at.isoformat() if patient.created_at else None,
            )
            for patient, appointment_count in rows
        ]
