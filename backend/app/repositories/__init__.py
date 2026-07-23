from app.repositories.admin import (
    AdminUserRepository,
    AdminSpecializationRepository,
    AdminSlotRepository,
    AdminClinicRepository,
    AdminPatientRepository,
    AdminDashboardRepository,
)
from app.repositories.doctor import (
    DoctorAvailabilityRepository,
    DoctorAppointmentRepository,
    DoctorPrescriptionRepository,
    DoctorWalkInRepository,
    DoctorProfileRepository,
    DoctorDashboardRepository,
)
from app.repositories.frontdesk import (
    FrontdeskPatientRepository,
    FrontdeskAppointmentRepository,
    FrontdeskAvailabilityRepository,
    FrontdeskWalkInRepository,
    FrontdeskDashboardRepository,
)
from app.repositories.public import (
    PublicDoctorRepository,
    PublicBookingRepository,
    PublicOTPRepository,
    PublicContactRepository,
    PublicPrescriptionRepository,
)
from app.repositories.notification_repository import NotificationRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "UserRepository",
    "RoleRepository",
    "NotificationRepository",
    "AdminUserRepository",
    "AdminSpecializationRepository",
    "AdminSlotRepository",
    "AdminClinicRepository",
    "AdminPatientRepository",
    "AdminDashboardRepository",
    "DoctorAvailabilityRepository",
    "DoctorAppointmentRepository",
    "DoctorPrescriptionRepository",
    "DoctorWalkInRepository",
    "DoctorProfileRepository",
    "DoctorDashboardRepository",
    "FrontdeskPatientRepository",
    "FrontdeskAppointmentRepository",
    "FrontdeskAvailabilityRepository",
    "FrontdeskWalkInRepository",
    "FrontdeskDashboardRepository",
    "PublicDoctorRepository",
    "PublicBookingRepository",
    "PublicOTPRepository",
    "PublicContactRepository",
    "PublicPrescriptionRepository",
]
