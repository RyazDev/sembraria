"""
SembrarIA - FastAPI app entrypoint.

Middlewares (orden importa):
1. SecurityHeaders: agrega headers de seguridad a todas las respuestas
2. RequestID: asigna X-Request-Id y loguea cada peticion
3. SlowAPI: rate limiting (en app.state, no como middleware ASGI)
4. CORSMiddleware: maneja CORS preflight y headers
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from sembraria.api import (
    alerts,
    analysis,
    audit,
    auth,
    catalog,
    farms,
    health,
    notifications,
    prices,
    reports,
    results,
)
from sembraria.config import get_settings
from sembraria.init_db import init_db
from sembraria.middleware import RequestIDMiddleware
from sembraria.rate_limit import limiter, rate_limit_exceeded_handler
from sembraria.security_middleware import SecurityHeadersMiddleware

settings = get_settings()


# === Logging estructurado ===
logging.basicConfig(
    level=settings.log_level,
    format=(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        if settings.log_format == "detailed"
        else "%(levelname)s: %(message)s"
    ),
)
logger = logging.getLogger(__name__)


# === Lifespan (startup/shutdown) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: inicializa DB. Shutdown: cleanup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    if settings.app_env != "production":
        try:
            init_db()
        except Exception as e:
            logger.error(f"Error en init_db: {e}")
    yield
    logger.info("Shutting down...")


# === App ===
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para analisis de aptitud agricola en Caqueta, Colombia. "
        "Usa datos satelitales Copernicus para identificar areas aptas "
        "para cacao, platano y yuca. **Datos de demo sinteticos**."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={"name": "Universidad de la Amazonia", "email": "noreply@sembriaia.udla.edu.co"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "health", "description": "Health checks del sistema"},
        {"name": "auth", "description": "Registro, login, gestion de sesion"},
        {"name": "farms", "description": "CRUD de fincas con geometria PostGIS"},
        {"name": "analysis", "description": "Ejecuta y consulta analisis de aptitud"},
        {"name": "results", "description": "Resultados: PNG, criterios, resumen"},
        {"name": "alerts", "description": "Alertas climaticas, deforestacion, precios"},
        {"name": "reports", "description": "Genera y descarga reportes PDF"},
        {"name": "prices", "description": "Precios de mercado (FEDECACAO, etc.)"},
        {"name": "catalog", "description": "Catalogos: cultivos, geofence, raster"},
        {"name": "notifications", "description": "Envio de email/SMS (mock por defecto)"},
        {"name": "audit", "description": "Log de eventos sensibles (extensionistas+)"},
    ],
)

# === Rate limiting (slowapi) ===
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# === Middlewares (orden: primero los mas externos) ===
# 1. Security headers (lo mas externo)
app.add_middleware(SecurityHeadersMiddleware, environment=settings.app_env)
# 2. Request ID logging
app.add_middleware(RequestIDMiddleware)
# 3. CORS (debe ser el ultimo para que vea los headers de los anteriores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id"],
)

# === Static files (para servir PNGs y PDFs generados) ===
outputs_path = settings.outputs_path
outputs_path.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.static_url_prefix,
    StaticFiles(directory=str(outputs_path)),
    name="static",
)

# === Routers ===
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(catalog.router, prefix=settings.api_prefix, tags=["catalog"])
app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(farms.router, prefix=f"{settings.api_prefix}/farms", tags=["farms"])
app.include_router(analysis.router, prefix=f"{settings.api_prefix}/analysis", tags=["analysis"])
app.include_router(results.router, prefix=f"{settings.api_prefix}/results", tags=["results"])
app.include_router(alerts.router, prefix=f"{settings.api_prefix}/alerts", tags=["alerts"])
app.include_router(reports.router, prefix=f"{settings.api_prefix}/reports", tags=["reports"])
app.include_router(prices.router, prefix=f"{settings.api_prefix}/prices", tags=["prices"])
app.include_router(notifications.router, prefix=f"{settings.api_prefix}/notifications", tags=["notifications"])
app.include_router(audit.router, prefix=f"{settings.api_prefix}/audit", tags=["audit"])


# === Global exception handler ===
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.app_env == "development" else "An error occurred",
        },
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "data_provenance": "synthetic",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sembraria.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
    )
