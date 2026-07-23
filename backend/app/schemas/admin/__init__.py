from app.schemas.admin.dashboard import AdminDashboardResponse
from app.schemas.admin.user import (
    DoctorProfileInput,
    ManagementUserCreateRequest,
    ManagementUserResponse,
    ManagementUserUpdateRequest,
    UserStatusUpdateRequest,
)
from app.schemas.admin.specialization import SpecializationCreateRequest, SpecializationResponse
from app.schemas.admin.slot import SlotCreateRequest, SlotResponse
from app.schemas.admin.clinic import ClinicSettingsUpsertRequest, ClinicSettingsResponse
from app.schemas.admin.patient import PatientListItemResponse
from app.schemas.admin.profile import AdminProfileResponse, AdminProfileUpdateRequest

__all__ = [
    "AdminDashboardResponse",
    "DoctorProfileInput",
    "ManagementUserCreateRequest",
    "ManagementUserResponse",
    "ManagementUserUpdateRequest",
    "UserStatusUpdateRequest",
    "SpecializationCreateRequest",
    "SpecializationResponse",
    "SlotCreateRequest",
    "SlotResponse",
    "ClinicSettingsUpsertRequest",
    "ClinicSettingsResponse",
    "PatientListItemResponse",
    "AdminProfileResponse",
    "AdminProfileUpdateRequest",
]
