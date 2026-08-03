from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.frontdesk.patient import FrontdeskPatientUpsertRequest
from app.schemas.validators import PHONE_NUMBER_PATTERN
from app.services.frontdesk.patient_service import FrontdeskPatientService

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


def _json_response(status_code: int, message: str, data: Any | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"status_code": status_code, "message": message, "data": data},
    )


@router.get("/patients/by-phone")
def get_patient_by_phone(
    phone: Annotated[str, Query(min_length=10, max_length=10, pattern=PHONE_NUMBER_PATTERN)],
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    result = FrontdeskPatientService(db).get_patient_by_phone(phone)
    return _json_response(result["status_code"], result["message"], result["data"])


@router.get("/patients/search")
def search_patients(
    q: str,
    limit: int = 10,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    result = FrontdeskPatientService(db).search_patients(q, limit)
    return _json_response(result["status_code"], result["message"], result["data"])


@router.post("/patients")
def upsert_patient(
    payload: FrontdeskPatientUpsertRequest,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    result = FrontdeskPatientService(db).upsert_patient(payload)
    return _json_response(result["status_code"], result["message"], result["data"])
