from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clinic import ClinicSetting


class AdminClinicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_clinic_settings(self) -> ClinicSetting | None:
        stmt = select(ClinicSetting).where(ClinicSetting.id == 1)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_clinic_settings(self, settings: ClinicSetting) -> ClinicSetting:
        self.db.add(settings)
        self.db.flush()
        return settings
