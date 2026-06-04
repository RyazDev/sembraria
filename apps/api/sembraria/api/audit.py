"""
Audit Log endpoints: consulta el registro de eventos.
Solo accesible para usuarios con role >= extensionista.
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import desc
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.database import get_db
from sembraria.models.audit_log import AuditLog
from sembraria.models.user import User

router = APIRouter()


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    details: Optional[dict] = None
    created_at: datetime

    @field_validator("details", mode="before")
    @classmethod
    def _coerce_details(cls, v):
        """
        Tolerancia defensiva: si por algun motivo `details` viene como
        string (datos antiguos o un driver que devolvio el JSONB como str),
        intentamos parsearlo. Si no se puede, devolvemos un dict con la
        representacion cruda para no romper la respuesta.
        """
        if v is None or isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return {"_raw": v}
        return v

    @field_validator("ip_address", mode="before")
    @classmethod
    def _coerce_ip(cls, v):
        if v is None or isinstance(v, str):
            return v
        return str(v)


def _require_audit_access(user: User):
    """Solo extensionistas, cooperativas y gobierno pueden ver el audit log."""
    if user.role.value not in ("extensionista", "cooperativa", "gobierno"):
        raise HTTPException(
            status_code=403,
            detail="No autorizado. Solo extensionistas, cooperativas y gobierno pueden ver el audit log.",
        )


@router.get("", response_model=List[AuditLogOut])
async def list_audit_log(
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista los eventos del audit log con filtros opcionales."""
    _require_audit_access(current_user)

    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if resource:
        q = q.filter(AuditLog.resource == resource)
    return [
        AuditLogOut.model_validate(e)
        for e in q.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset).all()
    ]


@router.get("/actions")
async def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las acciones unicas registradas (para construir filtros UI)."""
    _require_audit_access(current_user)
    actions = db.query(AuditLog.action).distinct().all()
    return {"actions": sorted([a[0] for a in actions if a[0]])}
