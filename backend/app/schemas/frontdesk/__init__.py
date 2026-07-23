from app.schemas.frontdesk.patient import (
    FrontdeskPatientUpsertRequest,
    FrontdeskPatientResponse,
    FrontdeskPatientSearchItemResponse,
)
from app.schemas.frontdesk.appointment import (
    FrontdeskBookAppointmentRequest,
    FrontdeskAppointmentResponse,
    FrontdeskCancelAppointmentRequest,
    FrontdeskAppointmentListItemResponse,
)
from app.schemas.frontdesk.walkin import (
    FrontdeskWalkInCreateRequest,
    FrontdeskWalkInStatusUpdateRequest,
    FrontdeskWalkInResponse,
    FrontdeskWalkInListItemResponse,
)
from app.schemas.frontdesk.availability import FrontdeskAvailabilityResponse, FrontdeskDoctorOptionResponse
from app.schemas.frontdesk.profile import FrontdeskProfileResponse, FrontdeskProfileUpdateRequest
from app.schemas.frontdesk.dashboard import FrontdeskDashboardResponse

__all__ = [
    "FrontdeskPatientUpsertRequest",
    "FrontdeskPatientResponse",
    "FrontdeskPatientSearchItemResponse",
    "FrontdeskBookAppointmentRequest",
    "FrontdeskAppointmentResponse",
    "FrontdeskCancelAppointmentRequest",
    "FrontdeskAppointmentListItemResponse",
    "FrontdeskWalkInCreateRequest",
    "FrontdeskWalkInStatusUpdateRequest",
    "FrontdeskWalkInResponse",
    "FrontdeskWalkInListItemResponse",
    "FrontdeskAvailabilityResponse",
    "FrontdeskDoctorOptionResponse",
    "FrontdeskProfileResponse",
    "FrontdeskProfileUpdateRequest",
    "FrontdeskDashboardResponse",
]
