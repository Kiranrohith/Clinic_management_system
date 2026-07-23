from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Patient


class AdminPatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_patients_with_appointment_counts(self) -> list[tuple[Patient, int]]:
        appointment_counts = (
            select(Appointment.patient_id, func.count(Appointment.appointment_id).label("appointment_count"))
            .group_by(Appointment.patient_id)
            .subquery()
        )
        stmt = (
            select(Patient, func.coalesce(appointment_counts.c.appointment_count, 0).label("appointment_count"))
            .outerjoin(appointment_counts, Patient.patient_id == appointment_counts.c.patient_id)
            .order_by(Patient.patient_id.desc())
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], int(row[1])) for row in rows]
