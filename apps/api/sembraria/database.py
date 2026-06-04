"""
SembrarIA - Configuracion de SQLAlchemy con GeoAlchemy2.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from sembraria.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """Dependency para obtener sesion de DB en endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
