"""
Modelo Farm.
"""
import enum
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from sembraria.database import Base


class FarmStatus(str, enum.Enum):
    ACTIVA = "activa"
    EN_ANALISIS = "en_analisis"
    INACTIVA = "inactiva"


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    municipio = Column(String(100), nullable=False, index=True)
    geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    area_ha = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(FarmStatus, name="farm_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=FarmStatus.ACTIVA,
        index=True,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="farms")
    analyses = relationship("Analysis", back_populates="farm", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="farm")
