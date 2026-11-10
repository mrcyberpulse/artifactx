import logging
from typing import Protocol

from app.core.config import get_settings

logger = logging.getLogger("artifactx.mail")


class Mailer(Protocol):
    def send_password_reset(self, to_email: str, reset_url: str) -> None: ...


class LogMailer:
    """Placeholder transport. Real SMTP delivery is added by replacing get_mailer().

    The reset link is written to logs only when ARTIFACTX_ENVIRONMENT=development.
    """

    def send_password_reset(self, to_email: str, reset_url: str) -> None:
        if get_settings().environment == "development":
            logger.warning("DEV ONLY password reset link for %s: %s", to_email, reset_url)
        else:
            logger.info("Password reset requested; no mail transport is configured.")


def get_mailer() -> Mailer:
    return LogMailer()
