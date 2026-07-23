from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import Gender


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"))
    dob: Mapped[date | None] = mapped_column(Date)
    blood_group: Mapped[str | None] = mapped_column(String(10))
    address: Mapped[str | None] = mapped_column(Text)
    emergency_contact: Mapped[str | None] = mapped_column(String(15))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient")
    waiting_entries: Mapped[list["WaitingList"]] = relationship("WaitingList", back_populates="patient")
    prescriptions: Mapped[list["Prescription"]] = relationship("Prescription", back_populates="patient")
    walkin_tokens: Mapped[list["WalkInToken"]] = relationship("WalkInToken", back_populates="patient")
