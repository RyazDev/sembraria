"""
SembrarIA - Configuracion centralizada via Pydantic Settings.
Lee variables de entorno del archivo .env en la raiz del proyecto.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz del proyecto (4 niveles arriba de este archivo: apps/api/sembraria/config.py -> ../../../../)
BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = BASE_DIR / "config"


class Settings(BaseSettings):
    """Configuracion de la aplicacion, leida desde .env en la raiz."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === App ===
    app_name: str = "SembrarIA"
    app_version: str = "1.0.0"
    app_env: str = "development"
    log_level: str = "INFO"
    log_format: str = "detailed"

    # === Database ===
    # El driver +psycopg2 fuerza a SQLAlchemy a usar psycopg2 (declarado en requirements.txt).
    # Si no defines DATABASE_URL en .env, se usara este valor como fallback.
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/sembraria"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "sembraria"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # === API ===
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # === Security ===
    # jwt_secret: clave ACTIVA con la que se FIRMAN los nuevos tokens.
    # previous_jwt_secret: clave ANTERIOR que todavia puede VERIFICAR tokens
    #   durante el periodo de gracia despues de una rotacion (default 24h).
    #   Si esta vacia, solo se usa jwt_secret.
    # jwt_key_id / previous_jwt_key_id: identificadores publicos (kid) que
    #   viajan en el payload del JWT. Sirven para identificar con que clave
    #   se firmo un token y para trazabilidad en logs.
    # jwt_rotated_at: timestamp ISO 8601 de la ultima rotacion. Si esta
    #   vacio, nunca se ha rotado.
    # IMPORTANTE: el campo se llama `jwt_secret` (no `secret_key`) para
    #   matchear la variable de entorno JWT_SECRET definida en .env.
    jwt_secret: str = "change-me-in-production"
    previous_jwt_secret: str = ""
    jwt_key_id: str = "v1"
    previous_jwt_key_id: str = ""
    jwt_rotated_at: str = ""
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"
    # Periodo de gracia (segundos) durante el cual la clave anterior sigue
    # aceptando tokens despues de una rotacion. 86400 = 24h.
    jwt_grace_seconds: int = 86400

    # === Paths ===
    data_dir: str = "./data"
    inputs_dir: str = "./data/inputs"
    outputs_dir: str = "./data/outputs"
    static_url_prefix: str = "/static"

    # === Notifications (mocks) ===
    smtp_mock: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "SembrarIA <noreply@sembriaia.local>"

    twilio_mock: bool = True
    twilio_sid: str = ""
    twilio_token: str = ""
    twilio_phone: str = ""

    # === Analysis ===
    analysis_default_cultivo: str = "cacao"
    analysis_timeout_seconds: int = 120
    hectares_per_pixel_demo: float = 25.0

    # === Rate limiting ===
    # Numero maximo de requests por minuto a /auth/login por IP.
    # 0 = deshabilitar (no recomendado en produccion).
    login_rate_limit_per_minute: int = 10

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def data_path(self) -> Path:
        """Absolute path to data directory."""
        p = Path(self.data_dir)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def inputs_path(self) -> Path:
        """Absolute path to inputs directory (GeoTIFFs)."""
        p = Path(self.inputs_dir)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def outputs_path(self) -> Path:
        """Absolute path to outputs directory (PNG/PDF)."""
        p = Path(self.outputs_dir)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuracion."""
    return Settings()


# === Constantes cargadas desde YAML ===

@lru_cache
def get_crops_config() -> dict:
    """Carga el catalogo de cultivos desde crops.yaml."""
    with open(CONFIG_DIR / "catalog" / "crops.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def get_geofence_config() -> dict:
    """Carga configuracion del geofence desde geofence.yaml."""
    with open(CONFIG_DIR / "catalog" / "geofence.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def get_raster_config() -> dict:
    """Carga configuracion de raster desde raster.yaml."""
    with open(CONFIG_DIR / "catalog" / "raster.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_raster_path(filename: str) -> Path:
    """Devuelve la ruta absoluta a un archivo de entrada."""
    return get_settings().inputs_path / filename


def get_output_path(subdir: str, filename: str) -> Path:
    """Devuelve la ruta absoluta a un archivo de salida."""
    out_dir = get_settings().outputs_path / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename
