from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin.specialization import SpecializationCreateRequest
from app.services.admin.specialization_service import AdminSpecializationService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/specializations")
def create_specialization(
    payload: SpecializationCreateRequest,
    current_user: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminSpecializationService(db).create_specialization(payload, actor_user_id=current_user.user_id)
    return success_response("Specialization created successfully.", data.model_dump())


@router.get("/specializations")
def list_specializations(
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminSpecializationService(db).list_specializations()
    return success_response("Specializations fetched successfully.", [item.model_dump() for item in data])
