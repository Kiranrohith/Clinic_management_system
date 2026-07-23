from pydantic import BaseModel


class FrontdeskDashboardResponse(BaseModel):
    todays_appointments: int
    todays_walkin_tokens: int
    waiting_patients: int
