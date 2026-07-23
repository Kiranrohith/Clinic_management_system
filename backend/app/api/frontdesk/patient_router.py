from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.frontdesk.patient import FrontdeskPatientUpsertRequest
from app.services.frontdesk.patient_service import FrontdeskPatientService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.get("/patients/by-phone")
def get_patient_by_phone(
    phone: str,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskPatientService(db).get_patient_by_phone(phone)
    return success_response("Patient fetched successfully.", data.model_dump())


@router.get("/patients/search")
def search_patients(
    q: str,
    limit: int = 10,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskPatientService(db).search_patients(q, limit)
    return success_response("Patients fetched successfully.", [item.model_dump() for item in data])


@router.post("/patients")
def upsert_patient(
    payload: FrontdeskPatientUpsertRequest,
    _: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = FrontdeskPatientService(db).upsert_patient(payload)
    return success_response("Patient saved successfully.", data.model_dump())
