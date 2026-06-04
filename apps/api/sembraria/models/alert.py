"""
Modelo Alert.
"""
import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from sembraria.database import Base


class AlertType(str, enum.Enum):
    ESTRES_HIDRICO = "estres_hidrico"
    DEFORESTACION = "deforestacion"
    PRECIO = "precio"
    CLIMA = "clima"
    NORMAL = "normal"


class AlertSeverity(str, enum.Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    farm_id = Column(
        UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True
    )
    type = Column(
        Enum(AlertType, name="alert_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    severity = Column(
        Enum(
            AlertSeverity,
            name="alert_severity",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=AlertSeverity.MEDIA,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    affected_hectares = Column(Numeric(10, 2), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    is_synthetic = Column(Boolean, nullable=False, default=True, index=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    read_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="alerts")
    farm = relationship("Farm", back_populates="alerts")
