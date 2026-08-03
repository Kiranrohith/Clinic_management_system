from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth.auth import ChangePasswordRequest, LoginRequest, RefreshTokenRequest
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def _json_response(status_code: int, message: str, data: Any | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status_code": status_code, "message": message, "data": data})


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).login(payload.email, payload.password)
        return _json_response(status.HTTP_200_OK, "Login successful.", result.model_dump())
    except ValueError as exc:
        return _json_response(status.HTTP_401_UNAUTHORIZED, str(exc))
    except PermissionError as exc:
        return _json_response(status.HTTP_403_FORBIDDEN, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/token", include_in_schema=False)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        result = AuthService(db).login(form_data.username, form_data.password)
        return _json_response(status.HTTP_200_OK, "Login successful.", result.model_dump())
    except ValueError as exc:
        return _json_response(status.HTTP_401_UNAUTHORIZED, str(exc))
    except PermissionError as exc:
        return _json_response(status.HTTP_403_FORBIDDEN, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.get("/me")
def me(current_user: User = Depends(get_current_active_user)):
    try:
        return _json_response(status.HTTP_200_OK, "Current user fetched successfully.", AuthService.get_user_summary(current_user).model_dump())
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        AuthService(db).change_password(
            user_id=current_user.user_id,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
        return _json_response(status.HTTP_200_OK, "Password changed successfully.", None)
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except ValueError as exc:
        return _json_response(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).refresh(payload.refresh_token)
        return _json_response(status.HTTP_200_OK, "Token refreshed successfully.", result.model_dump())
    except ValueError as exc:
        return _json_response(status.HTTP_401_UNAUTHORIZED, str(exc))
    except LookupError as exc:
        return _json_response(status.HTTP_404_NOT_FOUND, str(exc))
    except PermissionError as exc:
        return _json_response(status.HTTP_403_FORBIDDEN, str(exc))
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    try:
        AuthService.logout(current_user)
        return _json_response(status.HTTP_200_OK, "Logout successful.", None)
    except Exception as exc:
        return _json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))
