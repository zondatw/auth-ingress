from __future__ import annotations

from email.message import EmailMessage
import smtplib
import ssl
from typing import Protocol

from auth_entry_portal.config import Settings


class RecoveryDelivery(Protocol):
    def send(self, recipient: str, link: str) -> None: ...


class RecoveryDeliveryError(RuntimeError):
    pass


class SMTPRecoveryDelivery:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, recipient: str, link: str) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_sender:
            raise RecoveryDeliveryError("Recovery delivery is not configured")
        message = EmailMessage()
        message["Subject"] = "Auth Portal password setup"
        message["From"] = self.settings.smtp_sender
        message["To"] = recipient
        message.set_content(f"Open this single-use link before it expires:\n\n{link}\n")
        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=self.settings.smtp_timeout_seconds) as client:
                if self.settings.smtp_starttls:
                    client.starttls(context=ssl.create_default_context())
                if self.settings.smtp_username:
                    client.login(self.settings.smtp_username, self.settings.smtp_password)
                client.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            raise RecoveryDeliveryError("Recovery delivery failed") from error
