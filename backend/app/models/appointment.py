from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import AppointmentStatus, BookingSource, WaitingStatus, WalkInStatus


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_patient_id", "patient_id"),
        Index("ix_appointments_availability_id", "availability_id"),
        Index("ix_appointments_appointment_status", "appointment_status"),
    )

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    availability_id: Mapped[int] = mapped_column(
        ForeignKey("doctor_availability.availability_id"),
        nullable=False,
    )
    booking_source: Mapped[BookingSource | None] = mapped_column(
        Enum(BookingSource, name="booking_source"),
    )
    appointment_status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status"),
        default=AppointmentStatus.BOOKED,
    )
    booked_by_phone: Mapped[str | None] = mapped_column(String(15))
    booked_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    availability: Mapped["DoctorAvailability"] = relationship(
        "DoctorAvailability",
        back_populates="appointments",
    )
    booked_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="booked_appointments",
        foreign_keys=[booked_by_user_id],
    )
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_appointments",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_appointments",
        foreign_keys=[updated_by],
    )
    prescription: Mapped["Prescription | None"] = relationship(
        "Prescription",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )


class WaitingList(Base):
    __tablename__ = "waiting_list"
    __table_args__ = (
        UniqueConstraint("availability_id", "position"),
    )

    waiting_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    availability_id: Mapped[int] = mapped_column(
        ForeignKey("doctor_availability.availability_id"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[WaitingStatus] = mapped_column(
        Enum(WaitingStatus, name="waiting_status"),
        default=WaitingStatus.WAITING,
    )
    notified_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="waiting_entries")
    availability: Mapped["DoctorAvailability"] = relationship(
        "DoctorAvailability",
        back_populates="waiting_entries",
    )


class WalkInToken(Base):
    __tablename__ = "walk_in_tokens"
    __table_args__ = (
        UniqueConstraint("doctor_user_id", "token_date", "token_number"),
    )

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_number: Mapped[int] = mapped_column(Integer, nullable=False)
    token_date: Mapped[date] = mapped_column(Date, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    doctor_user_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.doctor_user_id"),
        nullable=False,
    )
    status: Mapped[WalkInStatus] = mapped_column(
        Enum(WalkInStatus, name="walk_in_status"),
        default=WalkInStatus.WAITING,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="walkin_tokens")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="walkin_tokens")
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_walkin_tokens",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_walkin_tokens",
        foreign_keys=[updated_by],
    )
