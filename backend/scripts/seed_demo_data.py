from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import and_, select

from app.core.constants import ROLE_ADMIN, ROLE_DOCTOR, ROLE_FRONTDESK
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.doctor import Doctor, DoctorSpecialization, Specialization
from app.models.enums import SlotStatus, UserStatus
from app.models.schedule import DoctorAvailability, Slot
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.bootstrap_service import BootstrapService


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _get_or_create_user(
    user_repository: UserRepository,
    role_repository: RoleRepository,
    *,
    role_name: str,
    full_name: str,
    email: str,
    phone: str,
    password: str,
    actor_user_id: int,
    now: datetime,
) -> User:
    normalized_email = email.strip().lower()
    existing = user_repository.get_by_email(normalized_email)
    if existing is not None:
        if existing.role is None or existing.role.role_name != role_name:
            raise ValueError(f"Existing user {normalized_email} has non-matching role.")
        return existing

    role = role_repository.get_by_name(role_name)
    if role is None:
        raise ValueError(f"Role {role_name} does not exist.")

    user = User(
        role_id=role.role_id,
        full_name=full_name,
        email=normalized_email,
        phone=phone,
        password_hash=hash_password(password),
        status=UserStatus.ACTIVE,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        created_at=now,
        updated_at=now,
    )
    return user_repository.add(user)


def main() -> None:
    db = SessionLocal()
    try:
        bootstrap_service = BootstrapService(db)
        bootstrap_service.ensure_management_roles()

        user_repository = UserRepository(db)
        role_repository = RoleRepository(db)
        now = _now()

        admin_users = user_repository.list_by_role_names((ROLE_ADMIN,))
        if not admin_users:
            raise ValueError("No admin user found. Run bootstrap_auth first.")
        actor_user_id = admin_users[0].user_id

        created_users = []
        frontdesk_user = _get_or_create_user(
            user_repository,
            role_repository,
            role_name=ROLE_FRONTDESK,
            full_name="Ananya Frontdesk",
            email="frontdesk@carepoint.com",
            phone="9000000001",
            password="Frontdesk@123",
            actor_user_id=actor_user_id,
            now=now,
        )
        created_users.append(frontdesk_user.email)

        doctor_accounts = [
            {
                "full_name": "Dr. Arjun Mehta",
                "email": "doctor.arjun@carepoint.com",
                "phone": "9000000002",
                "password": "Doctor@123",
                "qualification": "MD Internal Medicine",
                "experience_years": 12,
                "consultation_fee": 700.0,
                "about": "Experienced internist focused on preventive and long-term care.",
                "specializations": ["General Medicine", "Diabetology"],
            },
            {
                "full_name": "Dr. Nisha Rao",
                "email": "doctor.nisha@carepoint.com",
                "phone": "9000000003",
                "password": "Doctor@123",
                "qualification": "MS Orthopaedics",
                "experience_years": 9,
                "consultation_fee": 900.0,
                "about": "Orthopaedic specialist in sports injuries and joint pain management.",
                "specializations": ["Orthopaedics"],
            },
        ]

        doctor_user_ids: list[int] = []
        for doctor_data in doctor_accounts:
            doctor_user = _get_or_create_user(
                user_repository,
                role_repository,
                role_name=ROLE_DOCTOR,
                full_name=doctor_data["full_name"],
                email=doctor_data["email"],
                phone=doctor_data["phone"],
                password=doctor_data["password"],
                actor_user_id=actor_user_id,
                now=now,
            )
            created_users.append(doctor_user.email)
            doctor_user_ids.append(doctor_user.user_id)

            existing_profile = db.execute(
                select(Doctor).where(Doctor.doctor_user_id == doctor_user.user_id)
            ).scalar_one_or_none()
            if existing_profile is None:
                db.add(
                    Doctor(
                        doctor_user_id=doctor_user.user_id,
                        qualification=doctor_data["qualification"],
                        experience_years=doctor_data["experience_years"],
                        consultation_fee=doctor_data["consultation_fee"],
                        about=doctor_data["about"],
                        created_by=actor_user_id,
                        updated_by=actor_user_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
                db.flush()

            for specialization_name in doctor_data["specializations"]:
                specialization = db.execute(
                    select(Specialization).where(
                        Specialization.specialization_name == specialization_name
                    )
                ).scalar_one_or_none()
                if specialization is None:
                    specialization = Specialization(
                        specialization_name=specialization_name,
                        created_by=actor_user_id,
                        updated_by=actor_user_id,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(specialization)
                    db.flush()

                existing_link = db.execute(
                    select(DoctorSpecialization).where(
                        and_(
                            DoctorSpecialization.doctor_user_id == doctor_user.user_id,
                            DoctorSpecialization.specialization_id == specialization.specialization_id,
                        )
                    )
                ).scalar_one_or_none()
                if existing_link is None:
                    db.add(
                        DoctorSpecialization(
                            doctor_user_id=doctor_user.user_id,
                            specialization_id=specialization.specialization_id,
                            created_by=actor_user_id,
                            updated_by=actor_user_id,
                            created_at=now,
                            updated_at=now,
                        )
                    )

        slot_ranges = [
            (time(9, 0), time(9, 15)),
            (time(9, 15), time(9, 30)),
            (time(9, 30), time(9, 45)),
            (time(9, 45), time(10, 0)),
            (time(10, 0), time(10, 15)),
            (time(10, 15), time(10, 30)),
            (time(10, 30), time(10, 45)),
            (time(10, 45), time(11, 0)),
        ]

        slot_ids: list[int] = []
        for start_time, end_time in slot_ranges:
            slot = db.execute(
                select(Slot).where(
                    and_(
                        Slot.slot_start_time == start_time,
                        Slot.slot_end_time == end_time,
                    )
                )
            ).scalar_one_or_none()
            if slot is None:
                slot = Slot(slot_start_time=start_time, slot_end_time=end_time, created_at=now)
                db.add(slot)
                db.flush()
            slot_ids.append(slot.slot_id)

        availability_created = 0
        for doctor_user_id in doctor_user_ids:
            for day_offset in range(5):
                available_date = date.today() + timedelta(days=day_offset)
                for slot_id in slot_ids:
                    existing_availability = db.execute(
                        select(DoctorAvailability).where(
                            and_(
                                DoctorAvailability.doctor_user_id == doctor_user_id,
                                DoctorAvailability.available_date == available_date,
                                DoctorAvailability.slot_id == slot_id,
                            )
                        )
                    ).scalar_one_or_none()
                    if existing_availability is not None:
                        continue

                    db.add(
                        DoctorAvailability(
                            doctor_user_id=doctor_user_id,
                            available_date=available_date,
                            slot_id=slot_id,
                            slot_status=SlotStatus.AVAILABLE,
                            created_by=actor_user_id,
                            updated_by=actor_user_id,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    availability_created += 1

        db.commit()

        print("Demo seed completed successfully.")
        print(f"Admin actor user_id: {actor_user_id}")
        print(f"Management users ensured: {', '.join(created_users)}")
        print(f"Slots ensured: {len(slot_ids)}")
        print(f"Availabilities newly created: {availability_created}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
