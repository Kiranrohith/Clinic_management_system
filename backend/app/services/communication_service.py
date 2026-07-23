import logging
from datetime import UTC, datetime

from app.core.config import settings

logger = logging.getLogger("clinic.communication")


class CommunicationService:
    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).replace(tzinfo=None).isoformat()

    def send_sms(self, phone: str, template_key: str, variables: dict[str, str]) -> dict[str, str]:
        payload = {
            "provider": settings.sms_provider,
            "sender_id": settings.sms_sender_id,
            "phone": phone,
            "template_key": template_key,
            "variables": variables,
            "sent_at": self._now_iso(),
        }
        if settings.sms_enabled:
            logger.info("SMS dispatch requested payload=%s", payload)
        else:
            logger.info("SMS disabled; mock dispatch payload=%s", payload)
        return {
            "status": "queued",
            "provider": settings.sms_provider,
            "template_key": template_key,
            "sent_at": payload["sent_at"],
        }
