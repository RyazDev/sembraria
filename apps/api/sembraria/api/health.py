"""
Health check endpoint - extendido.
Verifica:
- App
- DB (SELECT 1)
- Migraciones aplicadas
- Rasters de entrada (existen y son legibles)
- Espacio en disco del directorio de outputs
"""
import shutil
from datetime import datetime, timezone
from pathlib import Path

import rasterio
from fastapi import APIRouter
from sqlalchemy import text

from sembraria.config import (
    get_crops_config,
    get_raster_config,
    get_settings,
)
from sembraria.database import engine

router = APIRouter()


def _check_raster_file(path: Path) -> dict:
    """Inspecciona un raster: existencia, tamaño, bandas, nodata, dtype."""
    if not path.exists():
        return {"status": "missing", "path": str(path), "size_mb": 0}
    try:
        with rasterio.open(path) as src:
            size_mb = round(path.stat().st_size / (1024 * 1024), 2)
            return {
                "status": "ok",
                "path": str(path),
                "size_mb": size_mb,
                "bands": src.count,
                "width": src.width,
                "height": src.height,
                "crs": str(src.crs),
                "dtype": str(src.dtypes[0]),
                "nodata": src.nodata,
            }
    except Exception as e:
        return {"status": "error", "path": str(path), "error": str(e)}


def _check_db() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).fetchone()
            version = conn.execute(text("SELECT version()")).scalar()
            return {"status": "ok", "version": version}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_migrations() -> dict:
    """Cuenta cuantos scripts SQL se aplicaron."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT count(*) FROM _db_migrations")
            ).scalar()
            return {"status": "ok", "applied_count": int(result or 0)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_postgis() -> dict:
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT PostGIS_Version()")).scalar()
            return {"status": "ok", "version": str(version)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_disk_space(path: Path) -> dict:
    try:
        usage = shutil.disk_usage(path)
        return {
            "status": "ok",
            "path": str(path),
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent_used": round(usage.used / usage.total * 100, 1),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/health")
async def health():
    """
    Health check completo.
    Devuelve:
    - status: ok | degraded | error
    - app: { name, version, env }
    - database: { status, version, postgis_version, migrations_applied }
    - rasters: { name -> info }
    - disk: { outputs_path -> disk space }
    - timestamp: ISO 8601
    """
    settings = get_settings()
    raster_cfg = get_raster_config()
    crops_cfg = get_crops_config()

    db = _check_db()
    postgis = _check_postgis()
    migrations = _check_migrations()

    rasters = {}
    expected = [
        "aptitud_CACAO.tif",
        "aptitud_PLATANO.tif",
        "aptitud_YUCA.tif",
        "clasificacion_5clases.tif",
        "sintesis_mejor_cultivo.tif",
        "stack_54features.tif",
    ]
    for name in expected:
        path = settings.inputs_path / name
        rasters[name] = _check_raster_file(path)

    disk = _check_disk_space(settings.outputs_path)

    rasters_ok = all(r["status"] == "ok" for r in rasters.values())
    disk_ok = disk["status"] == "ok" and disk.get("percent_used", 100) < 95
    db_ok = db["status"] == "ok" and postgis["status"] == "ok"

    if not db_ok:
        overall = "error"
    elif not rasters_ok or not disk_ok:
        overall = "degraded"
    else:
        overall = "ok"

    return {
        "status": overall,
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "env": settings.app_env,
        },
        "database": {
            "status": db["status"] if db["status"] == "ok" else "error",
            "version": db.get("version"),
            "postgis_version": postgis.get("version") if postgis["status"] == "ok" else None,
            "migrations_applied": migrations.get("applied_count"),
        },
        "rasters": rasters,
        "disk": disk,
        "raster_config": {
            "demo_pixel_size_m": raster_cfg["raster"]["demo_pixel_size_m"],
            "expected_count": len(expected),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
async def readiness():
    """Readiness probe: solo verifica DB (para Kubernetes/Docker)."""
    db = _check_db()
    return {"ready": db["status"] == "ok", "database": db["status"]}


@router.get("/health/live")
async def liveness():
    """Liveness probe: solo verifica que el proceso responde."""
    return {"alive": True}
