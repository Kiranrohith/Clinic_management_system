"""initial schema

Revision ID: a0412ea68513
Revises: 
Create Date: 2026-07-19 17:38:15.402727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a0412ea68513'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    gender = postgresql.ENUM("MALE", "FEMALE", "OTHER", name="gender")
    user_status = postgresql.ENUM("ACTIVE", "INACTIVE", name="user_status")
    booking_source = postgresql.ENUM("ONLINE", "FRONTDESK", "WALKIN", name="booking_source")
    slot_status = postgresql.ENUM(
        "AVAILABLE",
        "BOOKED",
        "CANCELLED_BY_DOCTOR",
        "BLOCKED",
        name="slot_status",
    )
    appointment_status = postgresql.ENUM(
        "BOOKED",
        "COMPLETED",
        "CANCELLED_BY_PATIENT",
        "CANCELLED_BY_FRONTDESK",
        "CANCELLED_BY_DOCTOR",
        "NO_SHOW",
        name="appointment_status",
    )
    contact_status = postgresql.ENUM("NEW", "IN_PROGRESS", "CLOSED", name="contact_status")
    waiting_status = postgresql.ENUM(
        "WAITING",
        "NOTIFIED",
        "CONFIRMED",
        "EXPIRED",
        "CANCELLED",
        name="waiting_status",
    )
    otp_purpose = postgresql.ENUM(
        "BOOK_APPOINTMENT",
        "VIEW_PRESCRIPTION",
        "PASSWORD_RESET",
        name="otp_purpose",
    )
    walk_in_status = postgresql.ENUM(
        "WAITING",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
        name="walk_in_status",
    )
    otp_status = postgresql.ENUM("PENDING", "VERIFIED", "EXPIRED", name="otp_status")
    notification_type = postgresql.ENUM(
        "APPOINTMENT_BOOKED",
        "APPOINTMENT_CANCELLED",
        "APPOINTMENT_COMPLETED",
        "DOCTOR_EMERGENCY",
        "NEW_CONTACT_REQUEST",
        "FOLLOW_UP_REMINDER",
        "WAITING_LIST_AVAILABLE",
        name="notification_type",
    )

    for enum_obj in [
        gender,
        user_status,
        booking_source,
        slot_status,
        appointment_status,
        contact_status,
        waiting_status,
        otp_purpose,
        walk_in_status,
        otp_status,
        notification_type,
    ]:
        enum_obj.create(bind, checkfirst=True)

    op.create_table(
        "roles",
        sa.Column("role_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_name", sa.String(length=30), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=True, unique=True),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("gender", postgresql.ENUM(name="gender", create_type=False), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="user_status", create_type=False),
            nullable=True,
            server_default="ACTIVE",
        ),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "specializations",
        sa.Column("specialization_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("specialization_name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "doctors",
        sa.Column("doctor_user_id", sa.Integer(), sa.ForeignKey("users.user_id"), primary_key=True),
        sa.Column("qualification", sa.String(length=200), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("consultation_fee", sa.Numeric(), nullable=True),
        sa.Column("about", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "doctor_specializations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "doctor_user_id",
            sa.Integer(),
            sa.ForeignKey("doctors.doctor_user_id"),
            nullable=False,
        ),
        sa.Column(
            "specialization_id",
            sa.Integer(),
            sa.ForeignKey("specializations.specialization_id"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("doctor_user_id", "specialization_id", name="uq_doctor_specializations"),
    )

    op.create_table(
        "patients",
        sa.Column("patient_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=False, unique=True),
        sa.Column("gender", postgresql.ENUM(name="gender", create_type=False), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("blood_group", sa.String(length=10), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("emergency_contact", sa.String(length=15), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "slots",
        sa.Column("slot_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slot_start_time", sa.Time(), nullable=False),
        sa.Column("slot_end_time", sa.Time(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "doctor_availability",
        sa.Column("availability_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "doctor_user_id",
            sa.Integer(),
            sa.ForeignKey("doctors.doctor_user_id"),
            nullable=False,
        ),
        sa.Column("available_date", sa.Date(), nullable=False),
        sa.Column("slot_id", sa.Integer(), sa.ForeignKey("slots.slot_id"), nullable=False),
        sa.Column(
            "slot_status",
            postgresql.ENUM(name="slot_status", create_type=False),
            nullable=True,
            server_default="AVAILABLE",
        ),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint(
            "doctor_user_id",
            "available_date",
            "slot_id",
            name="uq_doctor_availability",
        ),
    )

    op.create_table(
        "appointments",
        sa.Column("appointment_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=False),
        sa.Column(
            "availability_id",
            sa.Integer(),
            sa.ForeignKey("doctor_availability.availability_id"),
            nullable=False,
        ),
        sa.Column(
            "booking_source",
            postgresql.ENUM(name="booking_source", create_type=False),
            nullable=True,
        ),
        sa.Column(
            "appointment_status",
            postgresql.ENUM(name="appointment_status", create_type=False),
            nullable=True,
            server_default="BOOKED",
        ),
        sa.Column("booked_by_phone", sa.String(length=15), nullable=True),
        sa.Column("booked_by_user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_availability_id", "appointments", ["availability_id"])
    op.create_index("ix_appointments_appointment_status", "appointments", ["appointment_status"])

    op.create_table(
        "waiting_list",
        sa.Column("waiting_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=False),
        sa.Column(
            "availability_id",
            sa.Integer(),
            sa.ForeignKey("doctor_availability.availability_id"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(name="waiting_status", create_type=False),
            nullable=True,
            server_default="WAITING",
        ),
        sa.Column("notified_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("availability_id", "position", name="uq_waiting_list"),
    )

    op.create_table(
        "prescriptions",
        sa.Column("prescription_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.appointment_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=False),
        sa.Column(
            "doctor_user_id",
            sa.Integer(),
            sa.ForeignKey("doctors.doctor_user_id"),
            nullable=False,
        ),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("medicines", sa.Text(), nullable=True),
        sa.Column("dosage", sa.Text(), nullable=True),
        sa.Column("frequency", sa.Text(), nullable=True),
        sa.Column("duration", sa.String(length=100), nullable=True),
        sa.Column("doctor_advice", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("follow_up_reminder_sent", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
    )
    op.create_index("ix_prescriptions_patient_id", "prescriptions", ["patient_id"])
    op.create_index("ix_prescriptions_doctor_user_id", "prescriptions", ["doctor_user_id"])

    op.create_table(
        "walk_in_tokens",
        sa.Column("token_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_number", sa.Integer(), nullable=False),
        sa.Column("token_date", sa.Date(), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=False),
        sa.Column(
            "doctor_user_id",
            sa.Integer(),
            sa.ForeignKey("doctors.doctor_user_id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(name="walk_in_status", create_type=False),
            nullable=True,
            server_default="WAITING",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint(
            "doctor_user_id",
            "token_date",
            "token_number",
            name="uq_walk_in_tokens",
        ),
    )

    op.create_table(
        "otp_verifications",
        sa.Column("otp_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column(
            "purpose",
            postgresql.ENUM(name="otp_purpose", create_type=False),
            nullable=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(name="otp_status", create_type=False),
            nullable=True,
            server_default="PENDING",
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_otp_verifications_phone", "otp_verifications", ["phone"])
    op.create_index("ix_otp_verifications_purpose", "otp_verifications", ["purpose"])

    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column(
            "notification_type",
            postgresql.ENUM(name="notification_type", create_type=False),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=150), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "contact_queries",
        sa.Column("contact_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("subject", sa.String(length=200), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(name="contact_status", create_type=False),
            nullable=True,
            server_default="NEW",
        ),
        sa.Column("handled_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_contact_queries_status", "contact_queries", ["status"])
    op.create_index("ix_contact_queries_phone", "contact_queries", ["phone"])

    op.create_table(
        "clinic_settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("clinic_name", sa.String(length=150), nullable=False),
        sa.Column("clinic_phone", sa.String(length=15), nullable=True),
        sa.Column("clinic_email", sa.String(length=120), nullable=True),
        sa.Column("clinic_address", sa.Text(), nullable=True),
        sa.Column("opening_time", sa.Time(), nullable=False),
        sa.Column("closing_time", sa.Time(), nullable=False),
        sa.Column("slot_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("booking_window_days", sa.Integer(), nullable=False, server_default=sa.text("5")),
        sa.Column("appointment_limit_per_day", sa.Integer(), nullable=False, server_default=sa.text("2")),
        sa.Column("morning_break_start", sa.Time(), nullable=True),
        sa.Column("morning_break_end", sa.Time(), nullable=True),
        sa.Column("lunch_break_start", sa.Time(), nullable=True),
        sa.Column("lunch_break_end", sa.Time(), nullable=True),
        sa.Column("evening_break_start", sa.Time(), nullable=True),
        sa.Column("evening_break_end", sa.Time(), nullable=True),
        sa.Column("slot_generation_done", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    op.drop_table("clinic_settings")
    op.drop_index("ix_contact_queries_phone", table_name="contact_queries")
    op.drop_index("ix_contact_queries_status", table_name="contact_queries")
    op.drop_table("contact_queries")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_otp_verifications_purpose", table_name="otp_verifications")
    op.drop_index("ix_otp_verifications_phone", table_name="otp_verifications")
    op.drop_table("otp_verifications")
    op.drop_table("walk_in_tokens")
    op.drop_index("ix_prescriptions_doctor_user_id", table_name="prescriptions")
    op.drop_index("ix_prescriptions_patient_id", table_name="prescriptions")
    op.drop_table("prescriptions")
    op.drop_table("waiting_list")
    op.drop_index("ix_appointments_appointment_status", table_name="appointments")
    op.drop_index("ix_appointments_availability_id", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_table("appointments")
    op.drop_table("doctor_availability")
    op.drop_table("slots")
    op.drop_table("patients")
    op.drop_table("doctor_specializations")
    op.drop_table("doctors")
    op.drop_table("specializations")
    op.drop_table("users")
    op.drop_table("roles")

    for enum_name, values in [
        ("notification_type", ["APPOINTMENT_BOOKED", "APPOINTMENT_CANCELLED", "APPOINTMENT_COMPLETED", "DOCTOR_EMERGENCY", "NEW_CONTACT_REQUEST", "FOLLOW_UP_REMINDER", "WAITING_LIST_AVAILABLE"]),
        ("otp_status", ["PENDING", "VERIFIED", "EXPIRED"]),
        ("walk_in_status", ["WAITING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]),
        ("otp_purpose", ["BOOK_APPOINTMENT", "VIEW_PRESCRIPTION", "PASSWORD_RESET"]),
        ("waiting_status", ["WAITING", "NOTIFIED", "CONFIRMED", "EXPIRED", "CANCELLED"]),
        ("contact_status", ["NEW", "IN_PROGRESS", "CLOSED"]),
        ("appointment_status", ["BOOKED", "COMPLETED", "CANCELLED_BY_PATIENT", "CANCELLED_BY_FRONTDESK", "CANCELLED_BY_DOCTOR", "NO_SHOW"]),
        ("slot_status", ["AVAILABLE", "BOOKED", "CANCELLED_BY_DOCTOR", "BLOCKED"]),
        ("booking_source", ["ONLINE", "FRONTDESK", "WALKIN"]),
        ("user_status", ["ACTIVE", "INACTIVE"]),
        ("gender", ["MALE", "FEMALE", "OTHER"]),
    ]:
        postgresql.ENUM(*values, name=enum_name).drop(bind, checkfirst=True)
