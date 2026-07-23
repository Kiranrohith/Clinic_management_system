from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.role_name == role_name)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, role_name: str) -> Role:
        now = datetime.now(UTC).replace(tzinfo=None)
        role = Role(role_name=role_name, created_at=now, updated_at=now)
        self.db.add(role)
        self.db.flush()
        return role
