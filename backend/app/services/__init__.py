from app.services.admin import (
    AdminDashboardService,
    AdminUserService,
    AdminSpecializationService,
    AdminSlotService,
    AdminClinicService,
    AdminPatientService,
    AdminProfileService,
)
from app.services.auth.auth_service import AuthService
from app.services.bootstrap_service import BootstrapService
from app.services.doctor import (
    DoctorDashboardService,
    DoctorAvailabilityService,
    DoctorAppointmentService,
    DoctorPrescriptionService,
    DoctorProfileService,
)
from app.services.frontdesk import (
    FrontdeskDashboardService,
    FrontdeskPatientService,
    FrontdeskAppointmentService,
    FrontdeskWalkInService,
    FrontdeskProfileService,
)
from app.services.public import (
    PublicDoctorService,
    PublicBookingService,
    PublicOTPService,
    PublicContactService,
)
from app.services.notification_service import NotificationService

__all__ = [
    "AdminDashboardService",
    "AdminUserService",
    "AdminSpecializationService",
    "AdminSlotService",
    "AdminClinicService",
    "AdminPatientService",
    "AdminProfileService",
    "AuthService",
    "BootstrapService",
    "DoctorDashboardService",
    "DoctorAvailabilityService",
    "DoctorAppointmentService",
    "DoctorPrescriptionService",
    "DoctorProfileService",
    "FrontdeskDashboardService",
    "FrontdeskPatientService",
    "FrontdeskAppointmentService",
    "FrontdeskWalkInService",
    "FrontdeskProfileService",
    "PublicDoctorService",
    "PublicBookingService",
    "PublicOTPService",
    "PublicContactService",
    "NotificationService",
]
