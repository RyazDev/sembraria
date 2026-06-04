"""
Modelo AuditLog: registro append-only de eventos sensibles.

Cada vez que un usuario hace login, crea una finca, lanza un analisis,
o marca una alerta, se genera una fila aqui. Es la fuente de verdad
para responder preguntas como:
  - Quien elimino la finca X?
  - Cuando se logueo por ultima vez el usuario Y?
  - Que analisis se corrieron en la ultima semana?

La tabla es append-only: NO se debe UPDATE ni DELETE.
"""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID

from sembraria.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(64), nullable=False, index=True)
    resource = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=True, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(64), nullable=True, index=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )


# Indices compuestos para queries frecuentes
Index("idx_audit_user_created", AuditLog.user_id, AuditLog.created_at.desc())
Index("idx_audit_resource", AuditLog.resource, AuditLog.resource_id)
Index("idx_audit_action_created", AuditLog.action, AuditLog.created_at.desc())
