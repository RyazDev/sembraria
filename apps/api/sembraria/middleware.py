"""
SembrarIA - Middleware de logging estructurado y trazabilidad por request.

Para cada peticion HTTP:
- Asigna un request_id (UUID) si el cliente no envio X-Request-Id.
- Loguea entrada y salida con metodo, path, status, duracion.
- Agrega X-Request-Id al response header para que el cliente pueda
  referenciarlo en tickets de soporte.
"""
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sembraria.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Asigna X-Request-Id y mide la duracion de cada peticion."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        client_host = request.client.host if request.client else "-"
        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path} "
            f"from={client_host} ua={request.headers.get('user-agent', '-')[:80]}"
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                f"[{request_id}] !!! {request.method} {request.url.path} "
                f"failed after {duration_ms:.1f}ms: {exc}"
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-Id"] = request_id
        logger.info(
            f"[{request_id}] <-- {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration_ms:.1f}ms"
        )
        return response
