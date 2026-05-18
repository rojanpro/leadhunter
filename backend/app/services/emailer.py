import logging
import smtplib
from email.message import EmailMessage
from app.core.config import get_settings

log = logging.getLogger(__name__)


class EmailClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def configured(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_user and self.settings.smtp_password and self.settings.smtp_from_email)

    def send_email(self, to_email: str, subject: str, body: str) -> str:
        if not self.configured():
            raise RuntimeError("SMTP is not configured")
        msg = EmailMessage()
        msg["From"] = self.settings.smtp_from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        smtp_client = smtplib.SMTP_SSL if self.settings.smtp_port == 465 else smtplib.SMTP
        with smtp_client(self.settings.smtp_host, self.settings.smtp_port, timeout=30) as server:
            if self.settings.smtp_use_tls and self.settings.smtp_port != 465:
                server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.send_message(msg)
        return msg["Message-ID"] or f"smtp:{to_email}"
