from app.repositories.admin.user_repository import AdminUserRepository
from app.repositories.admin.specialization_repository import AdminSpecializationRepository
from app.repositories.admin.slot_repository import AdminSlotRepository
from app.repositories.admin.clinic_repository import AdminClinicRepository
from app.repositories.admin.patient_repository import AdminPatientRepository
from app.repositories.admin.dashboard_repository import AdminDashboardRepository

__all__ = [
    "AdminUserRepository",
    "AdminSpecializationRepository",
    "AdminSlotRepository",
    "AdminClinicRepository",
    "AdminPatientRepository",
    "AdminDashboardRepository",
]
