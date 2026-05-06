import smtplib
import asyncio
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from loguru import logger
from config.settings import settings


class EmailService:
    """Service d'envoi d'emails via SMTP (Gandi) émulant Roundcube."""

    def _get_plain_text(self, html: str) -> str:
        """Extrait le texte brut d'un contenu HTML."""
        return re.sub(r'<[^<]+?>', '', html).strip()

    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envoie un email HTML via SMTP Gandi à un destinataire unique."""
        return await asyncio.to_thread(self._send_sync, to_email, subject, html_content, False)

    def _send_sync(self, to_email: str, subject: str, html_content: str, is_broadcast: bool = False) -> bool:
        if not settings.smtp_user or not settings.smtp_password:
            logger.error("[EmailService] SMTP credentials missing.")
            return False
            
        try:
            # Emulation de Roundcube : multipart/alternative obligatoire
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain='goldarmyai.com')
            msg['User-Agent'] = 'Roundcube Webmail/1.5.0'  # Mimic Roundcube
            
            if is_broadcast:
                msg['Precedence'] = 'bulk'
                msg['List-Unsubscribe'] = f'<mailto:{settings.smtp_user}?subject=unsubscribe>'

            # Text and HTML parts
            plain_text = self._get_plain_text(html_content)
            part1 = MIMEText(plain_text, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)

            logger.info(f"[EmailService] Connecting to {settings.smtp_host}:{settings.smtp_port}")
            
            # Utilisation de SSL (Port 465)
            if settings.smtp_port == 465:
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)
            else:
                # Fallback TLS (Port 587)
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(msg)

            logger.info(f"[EmailService] SMTP Gandi OK → {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"[EmailService] SMTP Gandi FAILED → {to_email}: {e}")
            return False

    async def broadcast_email(self, user_emails: list, subject: str, html_content: str) -> int:
        """Envoie un email à une liste via SMTP Gandi."""
        success_count = 0
        for email in user_emails:
            ok = await asyncio.to_thread(self._send_sync, email, subject, html_content, True)
            if ok: 
                success_count += 1
            await asyncio.sleep(0.5) # Délai pour éviter le rate-limiting SMTP
            
        logger.info(f"[EmailService] Broadcast SMTP terminé: {success_count}/{len(user_emails)} envoyés.")
        return success_count


email_service = EmailService()
