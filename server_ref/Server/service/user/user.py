from sqlalchemy.orm import Session

from database.user.user import (
    create_user,
    get_users,
    get_user_by_id,
    get_user_by_email,
    update_user,
    delete_user,
)

from schema.user.user import (
    UserCreateRequestSchema,
    UserUpdateRequestSchema,
)

notifications = []
notification_count = 0
class UserService:
    def create_user(self, payload: UserCreateRequestSchema, db: Session):
        global notification_count
        result = create_user(db, payload)
        notification_count += 1
        notifications.append({
            "count": notification_count,
            "message": f"{payload.name} added successfully"
        })
        return result
    def get_users(self, db: Session):
        return get_users(db)

    def get_user_by_id(self, user_id, db: Session):
        return get_user_by_id(db, user_id)

    def get_user_by_email(self, email: str, db: Session):
        return get_user_by_email(db, email)

    def update_user(
        self,
        user,
        payload: UserUpdateRequestSchema,
        db: Session
    ):
        return update_user(db, user, payload)

    def delete_user(self, user, db: Session):
        return delete_user(db, user)


user_service = UserService()