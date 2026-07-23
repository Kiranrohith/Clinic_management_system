from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ClinicSetting(Base):
    __tablename__ = "clinic_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    clinic_name: Mapped[str] = mapped_column(String(150), nullable=False)
    clinic_phone: Mapped[str | None] = mapped_column(String(15))
    clinic_email: Mapped[str | None] = mapped_column(String(120))
    clinic_address: Mapped[str | None] = mapped_column(Text)
    opening_time: Mapped[time] = mapped_column(Time, nullable=False)
    closing_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_window_days: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    appointment_limit_per_day: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    morning_break_start: Mapped[time | None] = mapped_column(Time)
    morning_break_end: Mapped[time | None] = mapped_column(Time)
    lunch_break_start: Mapped[time | None] = mapped_column(Time)
    lunch_break_end: Mapped[time | None] = mapped_column(Time)
    evening_break_start: Mapped[time | None] = mapped_column(Time)
    evening_break_end: Mapped[time | None] = mapped_column(Time)
    slot_generation_done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_clinic_settings",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_clinic_settings",
        foreign_keys=[updated_by],
    )
