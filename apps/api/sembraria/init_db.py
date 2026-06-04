"""
SembrarIA - Init DB: corre los scripts SQL en config/db/ de forma idempotente.

Los scripts SQL son la fuente de verdad del esquema (tipos ENUM, tablas,
indices, funciones PostGIS, seed data). SQLAlchemy create_all() puede crear
los tipos ENUM que ya fueron creados por 02_schema.sql, por eso no usamos
create_all() aqui y dejamos que los .sql manejen todo de forma idempotente.

Se ejecuta al boot de FastAPI (ver main.py) y manualmente con:
    python -m sembraria.init_db
"""
import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from sembraria.config import CONFIG_DIR, get_settings
from sembraria.database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

INIT_DIR = CONFIG_DIR / "db"


def _script_already_applied(db, script_name: str) -> bool:
    """Detecta si un script ya fue aplicado, mirando la tabla _db_migrations.

    La tabla se crea automaticamente en el primer uso. Si el script ya esta
    registrado, lo saltamos para mantener idempotencia.
    """
    try:
        db.execute(text(
            "CREATE TABLE IF NOT EXISTS _db_migrations ("
            "  script_name VARCHAR(255) PRIMARY KEY,"
            "  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ");"
        ))
        db.commit()
        result = db.execute(
            text("SELECT 1 FROM _db_migrations WHERE script_name = :n"),
            {"n": script_name},
        ).first()
        return result is not None
    except SQLAlchemyError:
        db.rollback()
        return False


def _mark_script_applied(db, script_name: str) -> None:
    try:
        db.execute(
            text("INSERT INTO _db_migrations (script_name) VALUES (:n) ON CONFLICT DO NOTHING"),
            {"n": script_name},
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()


def run_init_scripts():
    """Ejecuta los scripts SQL en config/db/ en orden alfabetico, idempotente."""
    if not INIT_DIR.exists():
        logger.warning(f"Directorio db no encontrado: {INIT_DIR}")
        return

    sql_files = sorted(INIT_DIR.glob("*.sql"))
    if not sql_files:
        logger.warning("No se encontraron scripts SQL en db/")
        return

    db = SessionLocal()
    sql_file: Path | None = None
    try:
        for sql_file in sql_files:
            if _script_already_applied(db, sql_file.name):
                logger.info(f"Saltando {sql_file.name} (ya aplicado)")
                continue

            logger.info(f"Ejecutando {sql_file.name}...")
            sql_content = sql_file.read_text(encoding="utf-8")
            try:
                db.execute(text(sql_content))
                db.commit()
                _mark_script_applied(db, sql_file.name)
                logger.info(f"  OK: {sql_file.name}")
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error en {sql_file.name}: {e}")
                raise
    finally:
        db.close()


def init_db():
    """Pipeline: corre los scripts SQL idempotentes."""
    logger.info("=" * 60)
    logger.info("Inicializando base de datos SembrarIA...")
    logger.info("=" * 60)
    run_init_scripts()
    logger.info("=" * 60)
    logger.info("Base de datos lista.")
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
