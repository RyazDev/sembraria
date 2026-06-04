"""
Notification Service: mocks de email y SMS.
Por defecto loguea a consola. Si SMTP_USER/TWILIO_SID estan configurados,
usa el servicio real.

Todas las respuestas incluyen `mock` (bool) y `provider` (str) para que
el caller pueda mostrar claramente el estado del envio.
"""
import logging

from sembraria.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_email(to: str, subject: str, body: str) -> dict:
    """
    Envia email. Si SMTP_MOCK=true o SMTP_USER vacio, solo loguea.
    """
    if settings.smtp_mock or not settings.smtp_user:
        logger.info(f"[MOCK EMAIL] to={to} subject='{subject}' body='{body[:80]}...'")
        return {
            "ok": True,
            "mock": True,
            "channel": "email",
            "provider": "console-mock",
            "to": to,
            "subject": subject,
            "message": "Email mockeado (SMTP no configurado). Revisa la consola del backend.",
        }

    # Real SMTP
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.email_from
        msg["To"] = to

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        return {
            "ok": True,
            "mock": False,
            "channel": "email",
            "provider": f"smtp:{settings.smtp_host}",
            "to": to,
        }
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        return {"ok": False, "error": str(e), "channel": "email"}


def send_sms(to: str, body: str) -> dict:
    """
    Envia SMS. Si TWILIO_MOCK=true o TWILIO_SID vacio, solo loguea.
    """
    if settings.twilio_mock or not settings.twilio_sid:
        logger.info(f"[MOCK SMS] to={to} body='{body[:80]}...'")
        return {
            "ok": True,
            "mock": True,
            "channel": "sms",
            "provider": "console-mock",
            "to": to,
            "message": "SMS mockeado (Twilio no configurado). Revisa la consola del backend.",
        }

    # Real Twilio
    try:
        from twilio.rest import Client

        client = Client(settings.twilio_sid, settings.twilio_token)
        message = client.messages.create(
            body=body, from_=settings.twilio_phone, to=to
        )
        return {
            "ok": True,
            "mock": False,
            "channel": "sms",
            "provider": "twilio",
            "to": to,
            "sid": message.sid,
        }
    except Exception as e:
        logger.error(f"Error enviando SMS: {e}")
        return {"ok": False, "error": str(e), "channel": "sms"}
