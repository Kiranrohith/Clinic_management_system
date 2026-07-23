from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Specialization(Base):
    __tablename__ = "specializations"

    specialization_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    specialization_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_specializations",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_specializations",
        foreign_keys=[updated_by],
    )
    doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="specialization",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True,
    )
    qualification: Mapped[str | None] = mapped_column(String(200))
    experience_years: Mapped[int | None] = mapped_column(Integer)
    consultation_fee: Mapped[float | None] = mapped_column(Numeric)
    about: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="doctor_profile",
        foreign_keys=[doctor_user_id],
    )
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_doctor_profiles",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_doctor_profiles",
        foreign_keys=[updated_by],
    )
    doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="doctor",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        "DoctorAvailability",
        back_populates="doctor",
        foreign_keys="DoctorAvailability.doctor_user_id",
    )
    prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription",
        back_populates="doctor",
    )
    walkin_tokens: Mapped[list["WalkInToken"]] = relationship(
        "WalkInToken",
        back_populates="doctor",
    )


class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"
    __table_args__ = (UniqueConstraint("doctor_user_id", "specialization_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_user_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.doctor_user_id"),
        nullable=False,
    )
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey("specializations.specialization_id"),
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="doctor_specializations",
    )
    specialization: Mapped["Specialization"] = relationship(
        "Specialization",
        back_populates="doctor_specializations",
    )
    created_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_doctor_specializations",
        foreign_keys=[created_by],
    )
    updated_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_doctor_specializations",
        foreign_keys=[updated_by],
    )
