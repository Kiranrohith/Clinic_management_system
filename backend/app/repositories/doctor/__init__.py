from app.repositories.doctor.availability_repository import DoctorAvailabilityRepository
from app.repositories.doctor.appointment_repository import DoctorAppointmentRepository
from app.repositories.doctor.prescription_repository import DoctorPrescriptionRepository
from app.repositories.doctor.walkin_repository import DoctorWalkInRepository
from app.repositories.doctor.profile_repository import DoctorProfileRepository
from app.repositories.doctor.dashboard_repository import DoctorDashboardRepository

__all__ = [
    "DoctorAvailabilityRepository",
    "DoctorAppointmentRepository",
    "DoctorPrescriptionRepository",
    "DoctorWalkInRepository",
    "DoctorProfileRepository",
    "DoctorDashboardRepository",
]
