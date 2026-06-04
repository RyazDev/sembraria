"""
Modelo Result.

Trazabilidad: cada resultado registra la version del modelo/algoritmo
que lo produjo (model_version, model_algorithm), los rasters de
entrada (raster_inputs) y un snapshot de la config (config_snapshot).
Esto permite reproducir y auditar resultados historicos aunque el
codigo cambie.
"""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from sembraria.database import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    png_path = Column(String(500), nullable=True)
    pdf_path = Column(String(500), nullable=True)
    geojson_path = Column(String(500), nullable=True)
    png_url = Column(String(500), nullable=True)
    summary = Column(JSONB, nullable=True)
    criteria = Column(JSONB, nullable=True)
    slope_breakdown = Column(JSONB, nullable=True)
    # Trazabilidad del modelo/algoritmo
    model_version = Column(String(32), nullable=True, index=True)
    model_algorithm = Column(String(64), nullable=True)
    raster_inputs = Column(JSONB, nullable=True)
    config_snapshot = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis = relationship("Analysis", back_populates="result")
