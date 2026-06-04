"""
Schemas para Analysis.
"""
import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    """Body para POST /farms/{id}/analyze"""
    cultivo: str = Field(..., description="cacao | platano | yuca")


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    user_id: uuid.UUID
    cultivo: str
    status: str
    hectares_aptas: Optional[float] = None
    hectares_totales: Optional[float] = None
    porcentaje_apto: Optional[float] = None
    criterios: Optional[List[dict]] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisCreate(BaseModel):
    farm_id: uuid.UUID
    cultivo: str
