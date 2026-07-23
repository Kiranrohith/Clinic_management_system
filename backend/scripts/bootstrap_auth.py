from app.database.session import SessionLocal
from app.services.bootstrap_service import BootstrapService


def main() -> None:
    db = SessionLocal()
    try:
        service = BootstrapService(db)
        role_result = service.ensure_management_roles()
        admin_result = service.ensure_initial_admin()
        db.commit()

        print(f"Roles created: {role_result['created_roles']}")
        print(f"Roles existing: {role_result['existing_roles']}")
        print(f"Admin result: {admin_result}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
