from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.public.doctor_service import PublicDoctorService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/public", tags=["Public"])


@router.get("/health")
def health_check():
    return success_response("Service is healthy.", {"status": "ok"})


@router.get("/specializations")
def list_specializations(db: Session = Depends(get_db)):
    data = PublicDoctorService(db).list_specializations()
    return success_response("Specializations fetched successfully.", [item.model_dump() for item in data])


@router.get("/clinic-settings")
def get_clinic_settings(db: Session = Depends(get_db)):
    data = PublicDoctorService(db).get_clinic_settings()
    if data is None:
        return success_response("Clinic settings not configured yet.", {})
    return success_response("Clinic settings fetched successfully.", data.model_dump())


@router.get("/doctors")
def list_doctors(specialization_id: int | None = None, db: Session = Depends(get_db)):
    data = PublicDoctorService(db).list_doctors(specialization_id=specialization_id)
    return success_response("Doctors fetched successfully.", [item.model_dump() for item in data])


@router.get("/doctors/{doctor_user_id}")
def get_doctor(doctor_user_id: int, db: Session = Depends(get_db)):
    data = PublicDoctorService(db).get_doctor(doctor_user_id=doctor_user_id)
    return success_response("Doctor fetched successfully.", data.model_dump())


@router.get("/availabilities")
def list_availabilities(
    doctor_user_id: int | None = None,
    available_date: date | None = None,
    include_booked: bool = False,
    db: Session = Depends(get_db),
):
    data = PublicDoctorService(db).list_availabilities(
        doctor_user_id=doctor_user_id,
        available_date=available_date,
        include_booked=include_booked,
    )
    return success_response("Availabilities fetched successfully.", [item.model_dump() for item in data])
