from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Clinic Management System"
    debug: bool = False
    database_url: str = "postgresql+psycopg2://postgres:Berlin243@localhost:5432/CMS"
    secret_key: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7
    access_token_type: str = "bearer"
    public_otp_expire_minutes: int = 5
    public_otp_max_attempts: int = 5
    public_booking_session_minutes: int = 15
    sms_enabled: bool = False
    sms_provider: str = "mock"
    sms_sender_id: str = "CAREPOINT"
    bootstrap_admin_full_name: str | None = None
    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None
    bootstrap_admin_phone: str | None = None


settings = Settings()
