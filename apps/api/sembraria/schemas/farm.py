"""
Schemas para Farm. El campo `geom` se recibe/serializa como GeoJSON dict.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from shapely.geometry import mapping as shapely_mapping


class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    municipio: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class FarmCreate(FarmBase):
    """geom es un GeoJSON Polygon: {"type": "Polygon", "coordinates": [[[lng,lat],...]]}.
    area_ha es OPCIONAL: si no se envia, el servidor lo calcula desde la geometria.
    """
    geom: dict
    area_ha: Optional[float] = Field(None, gt=0, description="Opcional. Si se omite, se calcula del poligono.")

    @field_validator("geom")
    @classmethod
    def validate_geojson(cls, v: dict) -> dict:
        if v.get("type") != "Polygon":
            raise ValueError("geom debe ser un Polygon GeoJSON")
        coords = v.get("coordinates")
        if not coords or not isinstance(coords, list) or not coords[0]:
            raise ValueError("geom debe tener coordinates validas")
        for ring in coords:
            for point in ring:
                if not isinstance(point, list) or len(point) < 2:
                    raise ValueError("Cada punto debe ser [lng, lat]")
                if not (-180 <= point[0] <= 180):
                    raise ValueError("Longitud fuera de rango")
                if not (-90 <= point[1] <= 90):
                    raise ValueError("Latitud fuera de rango")
        return v


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    municipio: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class FarmOut(FarmBase):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: uuid.UUID
    user_id: uuid.UUID
    geom: Any
    area_ha: float
    status: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("geom")
    def serialize_geom(self, geom: Any) -> dict:
        """Convierte WKBElement (PostGIS) -> shapely -> GeoJSON dict."""
        if geom is None:
            return None
        if isinstance(geom, dict):
            return geom
        try:
            shape = to_shape(geom)
            return shapely_mapping(shape)
        except Exception:
            return str(geom)
