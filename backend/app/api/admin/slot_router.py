from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin.slot import SlotCreateRequest
from app.services.admin.slot_service import AdminSlotService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/slots/generate")
def generate_slots(
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminSlotService(db).generate_slots()
    return success_response("Slots generated successfully.", [item.model_dump() for item in data])


@router.delete("/slots/{slot_id}", status_code=200)
def delete_slot(
    slot_id: int,
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    AdminSlotService(db).delete_slot(slot_id)
    return success_response("Slot deleted successfully.", {})


@router.post("/slots")
def create_slot(
    payload: SlotCreateRequest,
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminSlotService(db).create_slot(payload)
    return success_response("Slot created successfully.", data.model_dump())


@router.get("/slots")
def list_slots(
    _: User = Depends(require_roles(ROLE_ADMIN)),
    db: Session = Depends(get_db),
):
    data = AdminSlotService(db).list_slots()
    return success_response("Slots fetched successfully.", [item.model_dump() for item in data])
