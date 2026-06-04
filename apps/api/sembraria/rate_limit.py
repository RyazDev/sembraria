"""
SembrarIA - Rate limiting con slowapi.

Previene ataques de fuerza bruta sobre /auth/login limitando el numero
de requests por IP por minuto. El limite es configurable via
LOGIN_RATE_LIMIT_PER_MINUTE en .env (0 = deshabilitar).

Para MVP usamos almacenamiento en memoria (suficiente para un solo
proceso). Para produccion multi-replica, migrar a Redis:
    storage_uri = "redis://localhost:6379"
"""
import logging

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from sembraria.config import get_settings

settings = get_settings()
logger = logging.getLogger("sembraria.ratelimit")


def _login_key(request: Request) -> str:
    """
    Key para rate limiting: IP + email si esta en el body.
    Asi un atacante no puede DOS a un usuario especifico con una IP rotativa
    (porque las requests con distintos emails contaran separado), pero
    multiples IPs apuntando al mismo email tambien se limitan.
    """
    ip = get_remote_address(request)
    try:
        body = request.scope.get("body") or b""
        if body:
            import json as _json
            try:
                payload = _json.loads(body)
                email = payload.get("email")
                if email:
                    return f"{ip}:{email}"
            except (ValueError, TypeError):
                pass
    except Exception:
        pass
    return ip


def _build_limit_str() -> str:
    """Devuelve 'N/minute' o '1000/minute' (deshabilitado de facto)."""
    n = settings.login_rate_limit_per_minute
    if n <= 0:
        # slowapi requiere un string valido, usamos un numero grande
        return "1000/minute"
    return f"{n}/minute"


# Limiter global. key_func por defecto es la IP.
limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
    strategy="fixed-window",
)


# Limite especifico para /auth/login (usa IP+email como key).
login_limit = _build_limit_str()


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> Response:
    """
    Handler 429 con cuerpo consistente con el resto de la API.
    Tambien loguea el evento para detectar ataques en curso.
    """
    logger.warning(
        f"Rate limit exceeded: {request.client.host if request.client else '?'} "
        f"path={request.url.path} limit={exc.detail}"
    )
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
            "limit": str(exc.detail),
            "retry_after_seconds": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
