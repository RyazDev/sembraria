"""
Schemas para Alert.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    farm_id: Optional[uuid.UUID] = None
    type: str
    severity: str
    title: str
    message: str
    affected_hectares: Optional[float] = None
    is_read: bool
    is_synthetic: bool
    metadata_: Optional[dict] = None
    created_at: datetime
    read_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    is_read: bool
