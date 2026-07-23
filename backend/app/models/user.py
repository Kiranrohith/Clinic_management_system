from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import Gender, UserStatus


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(15), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"))
    dob: Mapped[date | None] = mapped_column(Date)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"),
        default=UserStatus.ACTIVE,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    role: Mapped[Role] = relationship("Role", back_populates="users")
    creator: Mapped["User | None"] = relationship(
        "User",
        back_populates="created_users",
        foreign_keys=[created_by],
        remote_side=[user_id],
    )
    created_users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="creator",
        foreign_keys="User.created_by",
    )
    updater: Mapped["User | None"] = relationship(
        "User",
        back_populates="updated_users",
        foreign_keys=[updated_by],
        remote_side=[user_id],
    )
    updated_users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="updater",
        foreign_keys="User.updated_by",
    )

    doctor_profile: Mapped["Doctor | None"] = relationship(
        "Doctor",
        back_populates="user",
        foreign_keys="Doctor.doctor_user_id",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    created_doctor_profiles: Mapped[list["Doctor"]] = relationship(
        "Doctor",
        back_populates="created_by_user",
        foreign_keys="Doctor.created_by",
    )
    updated_doctor_profiles: Mapped[list["Doctor"]] = relationship(
        "Doctor",
        back_populates="updated_by_user",
        foreign_keys="Doctor.updated_by",
    )

    created_specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="created_by_user",
        foreign_keys="Specialization.created_by",
    )
    updated_specializations: Mapped[list["Specialization"]] = relationship(
        "Specialization",
        back_populates="updated_by_user",
        foreign_keys="Specialization.updated_by",
    )
    created_doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="created_by_user",
        foreign_keys="DoctorSpecialization.created_by",
    )
    updated_doctor_specializations: Mapped[list["DoctorSpecialization"]] = relationship(
        "DoctorSpecialization",
        back_populates="updated_by_user",
        foreign_keys="DoctorSpecialization.updated_by",
    )

    created_availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        "DoctorAvailability",
        back_populates="created_by_user",
        foreign_keys="DoctorAvailability.created_by",
    )
    updated_availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        "DoctorAvailability",
        back_populates="updated_by_user",
        foreign_keys="DoctorAvailability.updated_by",
    )

    booked_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="booked_by_user",
        foreign_keys="Appointment.booked_by_user_id",
    )
    created_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="created_by_user",
        foreign_keys="Appointment.created_by",
    )
    updated_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="updated_by_user",
        foreign_keys="Appointment.updated_by",
    )

    created_prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription",
        back_populates="created_by_user",
        foreign_keys="Prescription.created_by",
    )
    updated_prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription",
        back_populates="updated_by_user",
        foreign_keys="Prescription.updated_by",
    )

    created_walkin_tokens: Mapped[list["WalkInToken"]] = relationship(
        "WalkInToken",
        back_populates="created_by_user",
        foreign_keys="WalkInToken.created_by",
    )
    updated_walkin_tokens: Mapped[list["WalkInToken"]] = relationship(
        "WalkInToken",
        back_populates="updated_by_user",
        foreign_keys="WalkInToken.updated_by",
    )

    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
    handled_contact_queries: Mapped[list["ContactQuery"]] = relationship(
        "ContactQuery",
        back_populates="handled_by_user",
        foreign_keys="ContactQuery.handled_by",
    )

    created_clinic_settings: Mapped[list["ClinicSetting"]] = relationship(
        "ClinicSetting",
        back_populates="created_by_user",
        foreign_keys="ClinicSetting.created_by",
    )
    updated_clinic_settings: Mapped[list["ClinicSetting"]] = relationship(
        "ClinicSetting",
        back_populates="updated_by_user",
        foreign_keys="ClinicSetting.updated_by",
    )
