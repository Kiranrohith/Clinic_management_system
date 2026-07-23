from app.repositories.frontdesk.patient_repository import FrontdeskPatientRepository
from app.repositories.frontdesk.appointment_repository import FrontdeskAppointmentRepository
from app.repositories.frontdesk.availability_repository import FrontdeskAvailabilityRepository
from app.repositories.frontdesk.walkin_repository import FrontdeskWalkInRepository
from app.repositories.frontdesk.dashboard_repository import FrontdeskDashboardRepository

__all__ = [
    "FrontdeskPatientRepository",
    "FrontdeskAppointmentRepository",
    "FrontdeskAvailabilityRepository",
    "FrontdeskWalkInRepository",
    "FrontdeskDashboardRepository",
]
