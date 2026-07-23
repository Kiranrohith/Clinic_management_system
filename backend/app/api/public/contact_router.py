from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.public.contact import PublicContactQueryCreateRequest
from app.services.public.contact_service import PublicContactService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/public", tags=["Public"])


@router.post("/contact-queries")
def create_contact_query(payload: PublicContactQueryCreateRequest, db: Session = Depends(get_db)):
    data = PublicContactService(db).create_contact_query(payload)
    return success_response("Contact query submitted successfully.", data.model_dump())
