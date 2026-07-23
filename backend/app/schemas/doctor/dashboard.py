from pydantic import BaseModel


class DoctorDashboardResponse(BaseModel):
    todays_appointments: int
    completed_appointments: int
    pending_appointments: int
    todays_walkin_tokens: int
