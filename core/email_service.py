import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from config.settings import settings
from typing import Optional

class EmailService:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from

    async def send_otp(self, to_email: str, otp_code: str):
        subject = f"Votre code de vérification GoldArmy : {otp_code}"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #4F46E5; text-align: center;">Vérification GoldArmy</h2>
                    <p>Bonjour,</p>
                    <p>Voici votre code de vérification :</p>
                    <div style="background: #f4f4f4; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #4F46E5; border-radius: 5px; margin: 20px 0;">
                        {otp_code}
                    </div>
                </div>
            </body>
        </html>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False):
        if not self.user or not self.password:
            logger.info(f"SMTP Mock: Email to {to_email}")
            return True
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port)
            else:
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP Error: {e}")
            return False

email_service = EmailService()
