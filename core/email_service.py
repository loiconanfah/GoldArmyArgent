import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from loguru import logger
import asyncio

class EmailService:
    """Service d'envoi d'emails via SMTP."""

    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Envoie un email HTML à un destinataire unique."""
        if not settings.smtp_user or not settings.smtp_password:
            logger.warning("[EmailService] SMTP credentials missing. Email not sent.")
            return False

        # Run SMTP sending in a separate thread to avoid blocking the event loop
        return await asyncio.to_thread(self._send_sync, to_email, subject, html_content)

    def _send_sync(self, to_email: str, subject: str, html_content: str):
        try:
            logger.info(f"[EmailService] Attempting to send email to {to_email} via {settings.smtp_host}:{settings.smtp_port}")
            msg = MIMEMultipart()
            msg['From'] = settings.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(html_content, 'html'))

            # Handle SSL (465) vs TLS (587)
            if settings.smtp_port == 465:
                logger.info("[EmailService] Using SMTP_SSL (Port 465)")
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            else:
                logger.info(f"[EmailService] Using SMTP (Port {settings.smtp_port})")
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"[EmailService] Successfully sent email to {to_email}")
            return True
        except Exception as e:
            logger.error(f"[EmailService] FAILED to send email to {to_email}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def broadcast_email(self, user_emails: list, subject: str, html_content: str):
        """Envoie un email à une liste de destinataires."""
        tasks = [self.send_email(email, subject, html_content) for email in user_emails]
        results = await asyncio.gather(*tasks)
        return sum(1 for r in results if r)

email_service = EmailService()
