from sqlalchemy.orm import Session
from model.auth.auth import Auth
from schema.auth.auth import SignUpRequestSchema
def create_auth_user(db: Session,payload: SignUpRequestSchema,hashed_password: str):
    auth = Auth(email=payload.email,password=hashed_password)
    db.add(auth)
    db.commit()
    db.refresh(auth)
    return auth
def get_auth_user_by_email(db: Session,email: str):
    return (db.query(Auth).filter(Auth.email == email).first())