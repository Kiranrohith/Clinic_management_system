from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"
    __table_args__ = (
        Index("ix_prescriptions_patient_id", "patient_id"),
        Index("ix_prescriptions_doctor_user_id", "doctor_user_id"),
    )

    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.appointment_id"),
        unique=True,
        nullable=False,
    )
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    doctor_user_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_user_id"), nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    medicines: Mapped[str | None] = mapped_column(Text)
    dosage: Mapped[str | None] = mapped_column(Text)
    frequency: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[str | None] = mapped_column(String(100))
    doctor_advice: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    follow_up_reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))

    appointment: Mapped["Appointment"] = relationship(
        "Appointment",
        back_populates="prescription",
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="prescriptions")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="prescriptions")
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_prescriptions",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_prescriptions",
        foreign_keys=[updated_by],
    )
