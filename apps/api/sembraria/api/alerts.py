"""
Alerts endpoints: lista, marca como leidas.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.database import get_db
from sembraria.models.alert import Alert, AlertType
from sembraria.models.user import User
from sembraria.schemas.alert import AlertOut, AlertUpdate

router = APIRouter()


@router.get("", response_model=List[AlertOut])
async def list_alerts(
    type: Optional[AlertType] = None,
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las alertas del usuario actual."""
    q = db.query(Alert).filter(Alert.user_id == current_user.id)
    if type:
        q = q.filter(Alert.type == type)
    if is_read is not None:
        q = q.filter(Alert.is_read == is_read)
    return [AlertOut.model_validate(a) for a in q.order_by(Alert.created_at.desc()).all()]


@router.get("/unread-count")
async def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cuenta alertas no leidas."""
    count = (
        db.query(Alert)
        .filter(Alert.user_id == current_user.id, Alert.is_read == False)
        .count()
    )
    return {"unread": count}


@router.put("/{alert_id}/read", response_model=AlertOut)
async def mark_as_read(
    alert_id: uuid.UUID,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca una alerta como leida/no leida."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    if alert.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    alert.is_read = payload.is_read
    alert.read_at = datetime.now(timezone.utc) if payload.is_read else None
    db.commit()
    db.refresh(alert)
    return AlertOut.model_validate(alert)
