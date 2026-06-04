"""
Notifications endpoint: envio de email y SMS.

Trazabilidad:
  - Por defecto (SMTP_MOCK=true) el envio es MOCK: solo loguea en consola
    y devuelve `mock: true` en la respuesta.
  - Para envio real, configurar SMTP_USER, SMTP_PASSWORD, etc. en .env
    y poner SMTP_MOCK=false.
  - La respuesta siempre incluye `provider`, `mock` y `mode` para que
    el frontend muestre claramente el estado del envio.
"""
import os

from fastapi import APIRouter
from pydantic import BaseModel

from sembraria.config import get_settings
from sembraria.services.notification_service import send_email, send_sms

router = APIRouter()
settings = get_settings()


class NotificationRequest(BaseModel):
    to: str
    subject: str | None = None
    message: str
    channel: str = "email"  # email | sms


class NotificationStatus(BaseModel):
    """Estado del subsistema de notificaciones."""
    smtp_configured: bool
    smtp_host: str
    smtp_mock: bool
    twilio_configured: bool
    twilio_phone: str
    twilio_mock: bool
    mode: str  # "mock" | "live" | "mixed"


@router.get("/status", response_model=NotificationStatus)
async def notifications_status():
    """Devuelve el estado del subsistema de notificaciones.

    Util para que el frontend muestre un banner honesto:
    - mode='mock': todos los envios son simulados (no llegan al usuario)
    - mode='live': envio real configurado
    - mode='mixed': una parte es real, la otra no
    """
    smtp_configured = bool(
        not settings.smtp_mock and settings.smtp_user and settings.smtp_host
    )
    twilio_configured = bool(
        not settings.twilio_mock and settings.twilio_sid and settings.twilio_token
    )
    if smtp_configured and twilio_configured:
        mode = "live"
    elif smtp_configured or twilio_configured:
        mode = "mixed"
    else:
        mode = "mock"
    return NotificationStatus(
        smtp_configured=smtp_configured,
        smtp_host=settings.smtp_host if smtp_configured else "",
        smtp_mock=settings.smtp_mock,
        twilio_configured=twilio_configured,
        twilio_phone=settings.twilio_phone if twilio_configured else "",
        twilio_mock=settings.twilio_mock,
        mode=mode,
    )


@router.post("/notify-test")
async def notify_test(payload: NotificationRequest):
    """Envia una notificacion de prueba.

    Devuelve el resultado del envio incluyendo `mock` y `mode` para
    que el caller sepa si el mensaje realmente llego al destinatario.
    """
    if payload.channel == "email":
        result = send_email(
            to=payload.to,
            subject=payload.subject or "SembrarIA",
            body=payload.message,
        )
        result["mode"] = "live" if not settings.smtp_mock else "mock"
    elif payload.channel == "sms":
        result = send_sms(to=payload.to, body=payload.message)
        result["mode"] = "live" if not settings.twilio_mock else "mock"
    else:
        return {"ok": False, "error": f"Canal '{payload.channel}' no soportado"}

    return result
