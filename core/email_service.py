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

    async def send_otp(self, to_email: str, otp_code: str) -> bool:
        """Envoie un code OTP à un utilisateur pour vérification de compte."""
        subject = "Votre code de vérification GoldArmy"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f8fafc;">
            <div style="max-width: 600px; margin: 40px auto; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; padding: 32px;">
                <div style="text-align: center; margin-bottom: 24px;">
                    <h1 style="color: #f59e0b; margin: 0; font-size: 28px; font-weight: 800;">GOLDARMY</h1>
                    <p style="color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-top: 4px;">Sécurité & Authentification</p>
                </div>
                <div style="background-color: #0f172a; border-radius: 12px; padding: 24px; text-align: center; border: 1px solid #334155; margin-bottom: 24px;">
                    <p style="margin: 0 0 12px 0; color: #cbd5e1; font-size: 14px;">Voici votre code de vérification à 6 chiffres :</p>
                    <div style="font-size: 36px; font-weight: 900; letter-spacing: 8px; color: #f59e0b; margin: 12px 0;">{otp_code}</div>
                    <p style="margin: 12px 0 0 0; color: #64748b; font-size: 12px;">Ce code expire dans 10 minutes. Ne le partagez avec personne.</p>
                </div>
                <p style="color: #94a3b8; font-size: 13px; line-height: 1.5; margin: 0;">Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail en toute sécurité.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html)

    async def send_subscription_confirmation(self, to_email: str, tier_name: str) -> bool:
        """Envoie un e-mail de confirmation d'abonnement réussi."""
        tier_display = "GoldArmy Essentiel" if tier_name.upper() == "ESSENTIAL" else "GoldArmy Pro"
        subject = f"🎉 Activation de votre abonnement {tier_display}"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f8fafc;">
            <div style="max-width: 600px; margin: 40px auto; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; padding: 32px;">
                <div style="text-align: center; margin-bottom: 24px;">
                    <h1 style="color: #f59e0b; margin: 0; font-size: 28px; font-weight: 800;">GOLDARMY</h1>
                    <p style="color: #10b981; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-top: 6px;">Abonnement Confirmé</p>
                </div>
                <div style="background-color: #0f172a; border-radius: 12px; padding: 24px; border: 1px solid #334155; margin-bottom: 24px;">
                    <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">Félicitations !</h2>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                        Votre abonnement au forfait <strong style="color: #f59e0b;">{tier_display}</strong> a été activé avec succès.
                    </p>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                        Toutes vos nouvelles limites et fonctionnalités avancées sont disponibles immédiatement sur votre tableau de bord.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 28px;">
                    <a href="{settings.frontend_url}/settings" style="background-color: #f59e0b; color: #0f172a; text-decoration: none; font-weight: 800; font-size: 14px; padding: 14px 28px; border-radius: 10px; display: inline-block;">
                        Accéder à mes fonctionnalités
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html)

    async def send_subscription_cancellation(self, to_email: str) -> bool:
        """Envoie un e-mail de confirmation de résiliation d'abonnement."""
        subject = "Confirmation de résiliation de votre abonnement GoldArmy"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f8fafc;">
            <div style="max-width: 600px; margin: 40px auto; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; padding: 32px;">
                <div style="text-align: center; margin-bottom: 24px;">
                    <h1 style="color: #f59e0b; margin: 0; font-size: 28px; font-weight: 800;">GOLDARMY</h1>
                    <p style="color: #ef4444; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-top: 6px;">Résiliation d'Abonnement</p>
                </div>
                <div style="background-color: #0f172a; border-radius: 12px; padding: 24px; border: 1px solid #334155; margin-bottom: 24px;">
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                        Nous vous confirmons que votre abonnement GoldArmy a été annulé. Votre compte a été repassé en formule <strong>Gratuit</strong>.
                    </p>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                        Vous conservez l'accès à vos données existantes et vous pouvez vous réabonner à tout moment depuis vos paramètres.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 28px;">
                    <a href="{settings.frontend_url}/settings" style="background-color: #334155; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 24px; border-radius: 10px; display: inline-block;">
                        Voir mes paramètres
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html)

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
