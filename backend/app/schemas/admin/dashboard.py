from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    management_users: int
    doctors: int
    frontdesk: int
    patients: int
    appointments: int
