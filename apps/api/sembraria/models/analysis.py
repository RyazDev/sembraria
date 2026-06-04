"""
Modelo Analysis.
"""
import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from sembraria.database import Base


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cultivo = Column(String(50), nullable=False, index=True)
    status = Column(
        Enum(
            AnalysisStatus,
            name="analysis_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=AnalysisStatus.PENDING,
        index=True,
    )
    hectares_aptas = Column(Numeric(10, 2), nullable=True)
    hectares_totales = Column(Numeric(10, 2), nullable=True)
    porcentaje_apto = Column(Numeric(5, 2), nullable=True)
    criterios = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    farm = relationship("Farm", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
    result = relationship("Result", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
