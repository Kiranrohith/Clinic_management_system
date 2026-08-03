from sqlalchemy.orm import Session
from model.user.user import User
from schema.user.user import (UserCreateRequestSchema,UserUpdateRequestSchema,)

def create_user(db: Session,payload: UserCreateRequestSchema):
    new_user = User(
        name=payload.name,
        phone_number=payload.phone_number,
        email=payload.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
def get_users(db: Session):
    return ( db.query(User).filter(User.is_deleted == False).all() )
def get_user_by_id(db: Session,user_id):
    return ( db.query(User).filter(User.id == user_id, User.is_deleted == False ).first())
def get_user_by_email(db: Session,email: str):
    return (db.query(User).filter( User.email == email, User.is_deleted == False ).first() )
def update_user(db: Session,user: User,payload: UserUpdateRequestSchema):
    user.name = payload.name
    user.phone_number = payload.phone_number
    user.email = payload.email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session,user: User):
    user.is_deleted = True
    db.commit()
    return user