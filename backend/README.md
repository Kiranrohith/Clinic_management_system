## Authentication bootstrap

Use this command to seed management roles (`ADMIN`, `DOCTOR`, `FRONTDESK`) and create the first admin user.

```bash
uv run python scripts/bootstrap_auth.py
```

Required environment variables:

- `BOOTSTRAP_ADMIN_FULL_NAME`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`

Optional:

- `BOOTSTRAP_ADMIN_PHONE`

## Demo data seed

Use this command to seed reusable demo records for testing:

- one frontdesk user
- two doctor users with specializations and doctor profiles
- common slot master records
- next 5 days of doctor availability for seeded doctors

```bash
python -m scripts.seed_demo_data
```

Seeded login credentials:

- `frontdesk@carepoint.com` / `Frontdesk@123`
- `doctor.arjun@carepoint.com` / `Doctor@123`
- `doctor.nisha@carepoint.com` / `Doctor@123`

## OTP testing flow (current development mode)

Public OTP endpoints now use terminal output for testing:

1. User enters phone number in UI.
2. Backend generates OTP and stores it in database.
3. Backend prints OTP in server terminal.
4. Copy OTP from terminal and enter it in UI for verification.

Example output:

```text
Generated OTP (BOOK_APPOINTMENT) for 9876543210
OTP: 483912
```