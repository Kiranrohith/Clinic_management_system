from app.models.appointment import Appointment, WaitingList, WalkInToken
from app.models.clinic import ClinicSetting
from app.models.communication import ContactQuery, Notification, OTPVerification
from app.models.doctor import Doctor, DoctorSpecialization, Specialization
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import Role, User

__all__ = [
    "Role",
    "User",
    "Specialization",
    "Doctor",
    "DoctorSpecialization",
    "Patient",
    "Slot",
    "DoctorAvailability",
    "Appointment",
    "WaitingList",
    "Prescription",
    "WalkInToken",
    "OTPVerification",
    "Notification",
    "ContactQuery",
    "ClinicSetting",
]
