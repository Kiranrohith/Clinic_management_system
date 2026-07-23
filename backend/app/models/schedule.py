from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import SlotStatus


class Slot(Base):
    __tablename__ = "slots"

    slot_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_start_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_end_time: Mapped[time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        "DoctorAvailability",
        back_populates="slot",
    )


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    __table_args__ = (
        UniqueConstraint("doctor_user_id", "available_date", "slot_id"),
    )

    availability_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_user_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.doctor_user_id"),
        nullable=False,
    )
    available_date: Mapped[date] = mapped_column(Date, nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.slot_id"), nullable=False)
    slot_status: Mapped[SlotStatus] = mapped_column(
        Enum(SlotStatus, name="slot_status"),
        default=SlotStatus.AVAILABLE,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="availabilities",
        foreign_keys=[doctor_user_id],
    )
    slot: Mapped["Slot"] = relationship(
        "Slot",
        back_populates="availabilities",
    )
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_availabilities",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_availabilities",
        foreign_keys=[updated_by],
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="availability",
    )
    waiting_entries: Mapped[list["WaitingList"]] = relationship(
        "WaitingList",
        back_populates="availability",
    )
