"""
Modelo MarketPrice.

Trazabilidad:
  - `is_synthetic`: True si el dato fue generado por el seed o un script
    interno. False si viene de una fuente real (scraper de FEDECACAO, etc).
  - `source_url`: URL de la fuente real (NULL si sintetico).
  - `fetched_at`: cuando se descargo de la fuente real (NULL si sintetico).
"""
import uuid

from sqlalchemy import Boolean, Column, DateTime, Numeric, String, Text, func

from sembraria.database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto = Column(String(50), nullable=False, index=True)
    precio_cop_kg = Column(Numeric(12, 2), nullable=False)
    unidad = Column(String(20), nullable=False, default="COP/kg")
    fuente = Column(String(100), nullable=False)
    cambio_porcentual = Column(Numeric(5, 2), nullable=True)
    municipio = Column(String(100), nullable=True)
    recorded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    is_synthetic = Column(Boolean, nullable=False, default=True, index=True)
    source_url = Column(Text, nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=True)
