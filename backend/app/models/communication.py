from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ContactStatus, NotificationType, OTPPurpose, OTPStatus


class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    __table_args__ = (
        Index("ix_otp_verifications_phone", "phone"),
        Index("ix_otp_verifications_purpose", "purpose"),
    )

    otp_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    purpose: Mapped[OTPPurpose | None] = mapped_column(Enum(OTPPurpose, name="otp_purpose"))
    status: Mapped[OTPStatus] = mapped_column(
        Enum(OTPStatus, name="otp_status"),
        default=OTPStatus.PENDING,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
    )

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    notification_type: Mapped[NotificationType | None] = mapped_column(
        Enum(NotificationType, name="notification_type"),
    )
    title: Mapped[str | None] = mapped_column(String(150))
    message: Mapped[str | None] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class ContactQuery(Base):
    __tablename__ = "contact_queries"
    __table_args__ = (
        Index("ix_contact_queries_status", "status"),
        Index("ix_contact_queries_phone", "phone"),
    )

    contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120))
    subject: Mapped[str | None] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ContactStatus] = mapped_column(
        Enum(ContactStatus, name="contact_status"),
        default=ContactStatus.NEW,
    )
    handled_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    handled_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="handled_contact_queries",
        foreign_keys=[handled_by],
    )
