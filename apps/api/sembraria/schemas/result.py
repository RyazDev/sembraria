"""
Schemas para Result.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    analysis_id: uuid.UUID
    png_url: Optional[str] = None
    summary: Optional[dict] = None
    criteria: Optional[list] = None
    slope_breakdown: Optional[dict] = None
    # Trazabilidad: que version del modelo/algoritmo produjo este resultado
    model_version: Optional[str] = None
    model_algorithm: Optional[str] = None
    raster_inputs: Optional[list] = None
    config_snapshot: Optional[dict] = None
    created_at: datetime
