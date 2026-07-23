from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings


def _create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str) -> str:
    return _create_token(
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )


def create_refresh_token(subject: str, role: str) -> str:
    return _create_token(
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt_refresh_expire_days),
    )


def _decode_token(token: str, expected_token_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if token_type != expected_token_type:
        raise ValueError("Invalid token type")

    return payload


def decode_access_token(token: str) -> dict:
    return _decode_token(token=token, expected_token_type="access")


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token=token, expected_token_type="refresh")


def create_public_booking_token(phone: str) -> str:
    return _create_token(
        subject=phone,
        role="PUBLIC",
        token_type="public_booking",
        expires_delta=timedelta(minutes=settings.public_booking_session_minutes),
    )


def decode_public_booking_token(token: str) -> dict:
    return _decode_token(token=token, expected_token_type="public_booking")
