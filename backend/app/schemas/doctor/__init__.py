from app.schemas.doctor.dashboard import DoctorDashboardResponse
from app.schemas.doctor.availability import (
    DoctorAvailabilityCreateRequest,
    DoctorAvailabilityTimeWindowRequest,
    DoctorAvailabilityCancelRequest,
    DoctorAvailabilityResponse,
    DoctorAvailabilityTimeWindowResponse,
    DoctorSlotOptionResponse,
    DoctorEmergencyCancelRequest,
    DoctorEmergencyCancelResponse,
)
from app.schemas.doctor.prescription import (
    DoctorPrescriptionUpsertRequest,
    DoctorPrescriptionResponse,
    DoctorPrescriptionHistoryItemResponse,
)
from app.schemas.doctor.appointment import (
    DoctorCancelAppointmentRequest,
    DoctorPatientSummaryResponse,
    DoctorAppointmentResponse,
    DoctorAppointmentDetailResponse,
)
from app.schemas.doctor.walkin import DoctorWalkInResponse, DoctorWalkInStatusUpdateRequest
from app.schemas.doctor.profile import DoctorProfileResponse, DoctorProfileUpdateRequest

__all__ = [
    "DoctorDashboardResponse",
    "DoctorAvailabilityCreateRequest",
    "DoctorAvailabilityTimeWindowRequest",
    "DoctorAvailabilityCancelRequest",
    "DoctorAvailabilityResponse",
    "DoctorAvailabilityTimeWindowResponse",
    "DoctorSlotOptionResponse",
    "DoctorEmergencyCancelRequest",
    "DoctorEmergencyCancelResponse",
    "DoctorPrescriptionUpsertRequest",
    "DoctorPrescriptionResponse",
    "DoctorPrescriptionHistoryItemResponse",
    "DoctorCancelAppointmentRequest",
    "DoctorPatientSummaryResponse",
    "DoctorAppointmentResponse",
    "DoctorAppointmentDetailResponse",
    "DoctorWalkInResponse",
    "DoctorWalkInStatusUpdateRequest",
    "DoctorProfileResponse",
    "DoctorProfileUpdateRequest",
]
