"""
SembrarIA - Middleware de headers de seguridad.

Agrega headers HTTP recomendados por OWASP a todas las respuestas.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Headers de seguridad basicos (CSP, X-Frame-Options, etc.)."""

    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevenir MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS Protection (legacy pero util para navegadores antiguos)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permisos minimos
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        if self.environment == "production":
            # Solo habilitar HSTS en produccion (HTTPS obligatorio)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            # CSP estricta en produccion
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; script-src 'self'"
            )
        return response
