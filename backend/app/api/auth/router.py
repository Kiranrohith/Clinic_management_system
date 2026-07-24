from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth.auth import ChangePasswordRequest, LoginRequest, RefreshTokenRequest
from app.services.auth.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(payload.email, payload.password)
    return success_response("Login successful.", token.model_dump())


@router.post("/token", include_in_schema=False)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = AuthService(db).login(form_data.username, form_data.password)
    return {
        "access_token": token.access_token,
        "token_type": token.token_type,
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_active_user)):
    return success_response(
        "Current user fetched successfully.",
        AuthService.get_user_summary(current_user).model_dump(),
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    AuthService(db).change_password(
        user_id=current_user.user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return success_response("Password changed successfully.", {})


@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token = AuthService(db).refresh(payload.refresh_token)
    return success_response("Token refreshed successfully.", token.model_dump())


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    AuthService.logout(current_user)
    return success_response("Logout successful.", {})
