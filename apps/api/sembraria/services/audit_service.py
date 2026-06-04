"""
SembrarIA - Servicio de Audit Log.

Registra acciones sensibles (login, analisis creados, fincas modificadas,
alertas marcadas) en una tabla append-only. Esencial para trazabilidad
profesional y para responder a incidentes de seguridad.

Uso:
    from sembraria.services.audit_service import log_event
    log_event(db, user_id, "login", "auth", request=request)
"""
import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from sembraria.models.audit_log import AuditLog

logger = logging.getLogger("sembraria.audit")


def log_event(
    db: Session,
    *,
    user_id: Optional[str],
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    request: Optional[object] = None,
    details: Optional[dict] = None,
) -> Optional[AuditLog]:
    """
    Registra un evento en el audit log.

    Args:
        db: Sesion de SQLAlchemy.
        user_id: UUID del usuario que realizo la accion (None para anon).
        action: Verbo en pasado: 'login', 'logout', 'create_farm', etc.
        resource: Tipo de recurso: 'user', 'farm', 'analysis', 'alert', etc.
        resource_id: UUID del recurso afectado (None si no aplica).
        request: Objeto Request de FastAPI (opcional, para extraer IP, UA).
        details: Diccionario con metadata extra (no sensible).

    Returns:
        El registro AuditLog creado, o None si fallo.
    """
    try:
        ip_address = None
        user_agent = None
        request_id = None
        if request is not None:
            if hasattr(request, "client") and request.client:
                ip_address = request.client.host
            if hasattr(request, "headers"):
                user_agent = request.headers.get("user-agent", "")[:500]
            if hasattr(request, "state") and hasattr(request.state, "request_id"):
                request_id = request.state.request_id

        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details if details else None,
        )
        db.add(entry)
        db.commit()
        return entry
    except Exception as e:
        # Audit log NUNCA debe romper el flujo principal.
        # Si falla, logueamos el error pero dejamos que la operacion continue.
        logger.error(f"Error escribiendo audit log ({action}/{resource}): {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None
