from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import UserStatus
from app.models.user import Role, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_role_names(self, role_names: tuple[str, ...]) -> list[User]:
        stmt = (
            select(User)
            .join(Role, User.role_id == Role.role_id)
            .options(joinedload(User.role))
            .where(Role.role_name.in_(role_names))
            .order_by(User.user_id.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_active_user_ids_by_roles(self, role_names: tuple[str, ...]) -> list[int]:
        stmt = (
            select(User.user_id)
            .join(Role, User.role_id == Role.role_id)
            .where(
                Role.role_name.in_(role_names),
                User.status == UserStatus.ACTIVE,
            )
        )
        return [int(item) for item in self.db.execute(stmt).scalars().all()]

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def add(self, user: User) -> User:
        return self.create(user)

    def save(self, user: User) -> User:
        return self.create(user)
