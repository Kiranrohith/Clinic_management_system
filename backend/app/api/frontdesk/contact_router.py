from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ROLE_FRONTDESK
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.enums import ContactStatus
from app.models.user import User
from app.schemas.contact import ContactQueryUpdateRequest
from app.services.contact_query_service import ContactQueryService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/frontdesk", tags=["Frontdesk"])


@router.get("/contact-queries")
def list_contact_queries(
    status: ContactStatus | None = None,
    limit: int = 50,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = ContactQueryService(db).list_queries(
        actor_user_id=current_user.user_id,
        actor_role=current_user.role.role_name,
        status_filter=status,
        limit=limit,
    )
    return success_response("Contact queries fetched successfully.", [item.model_dump() for item in data])


@router.put("/contact-queries/{contact_id}")
def update_contact_query(
    contact_id: int,
    payload: ContactQueryUpdateRequest,
    current_user: User = Depends(require_roles(ROLE_FRONTDESK)),
    db: Session = Depends(get_db),
):
    data = ContactQueryService(db).update_query(
        actor_user_id=current_user.user_id,
        actor_role=current_user.role.role_name,
        contact_id=contact_id,
        payload=payload,
    )
    return success_response("Contact query updated successfully.", data.model_dump())
