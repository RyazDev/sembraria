"""
Farms endpoints: CRUD con geometria PostGIS.

El area_ha se calcula SIEMPRE en el servidor usando ST_Area con el CRS
proyectado adecuado (EPSG:3116 - MAGNA-Sirgas / Colombia Bogota).
Esto previene que el cliente envie un area_ha inconsistente con el
poligono real.

Todos los cambios quedan registrados en el audit log.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape
from sqlalchemy import text
from sqlalchemy.orm import Session

from sembraria.api.auth import get_current_user
from sembraria.config import get_geofence_config
from sembraria.database import get_db
from sembraria.models.farm import Farm
from sembraria.models.user import User
from sembraria.schemas.farm import FarmCreate, FarmOut, FarmUpdate
from sembraria.services.audit_service import log_event

router = APIRouter()


def _farm_to_geojson(farm: Farm) -> dict:
    if farm.geom is None:
        return None
    geom = to_shape(farm.geom)
    return {
        "type": "Polygon",
        "coordinates": [list(list(p) for p in geom.exterior.coords)],
    }


def _farm_to_out(farm: Farm) -> FarmOut:
    data = FarmOut.model_validate(farm).model_dump()
    data["geom"] = _farm_to_geojson(farm)
    return FarmOut(**data)


@router.get("", response_model=list[FarmOut])
async def list_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las fincas del usuario actual."""
    farms = (
        db.query(Farm)
        .filter(Farm.user_id == current_user.id)
        .order_by(Farm.created_at.desc())
        .all()
    )
    return [_farm_to_out(f) for f in farms]


@router.post("", response_model=FarmOut, status_code=201)
async def create_farm(
    payload: FarmCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva finca. El area_ha se calcula en el servidor desde el poligono."""
    try:
        polygon = shape(payload.geom)
        wkt = from_shape(polygon, srid=4326)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Geometria invalida: {e}")

    if not polygon.is_valid:
        raise HTTPException(
            status_code=400, detail="El poligono no es geometricamente valido"
        )

    result = db.execute(
        text("SELECT is_within_caqueta(ST_GeomFromText(:wkt, 4326))"),
        {"wkt": polygon.wkt},
    ).scalar()
    if not result:
        raise HTTPException(
            status_code=400,
            detail="La finca esta fuera del departamento de Caqueta. "
            "SembrarIA solo opera en Caqueta.",
        )

    geofence = get_geofence_config()["caqueta"]
    geofence_min = float(geofence.get("min_farm_ha", 0.1))
    geofence_max = float(geofence.get("max_farm_ha", 1000))
    area_crs = geofence.get("area_crs", "EPSG:3116")
    try:
        area_crs_epsg = int(area_crs.split(":")[-1])
    except (ValueError, AttributeError):
        area_crs_epsg = 3116

    area_ha = db.execute(
        text(
            "SELECT ST_Area(ST_Transform(ST_GeomFromText(:wkt, 4326), :crs)) / 10000.0"
        ),
        {"wkt": polygon.wkt, "crs": area_crs_epsg},
    ).scalar()
    area_ha = float(area_ha)

    if not (geofence_min <= area_ha <= geofence_max):
        raise HTTPException(
            status_code=400,
            detail=f"Area calculada ({area_ha:.2f} ha) fuera de rango. "
            f"Debe estar entre {geofence_min} y {geofence_max} ha.",
        )

    farm = Farm(
        user_id=current_user.id,
        name=payload.name,
        municipio=payload.municipio,
        geom=wkt,
        area_ha=area_ha,
        notes=payload.notes,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)

    log_event(
        db,
        user_id=str(current_user.id),
        action="create_farm",
        resource="farm",
        resource_id=str(farm.id),
        request=request,
        details={"name": farm.name, "municipio": farm.municipio, "area_ha": area_ha},
    )

    return _farm_to_out(farm)


@router.get("/{farm_id}", response_model=FarmOut)
async def get_farm(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una finca por ID."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if farm.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return _farm_to_out(farm)


@router.put("/{farm_id}", response_model=FarmOut)
async def update_farm(
    farm_id: uuid.UUID,
    payload: FarmUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una finca. Cambios quedan en audit log."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if farm.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)

    log_event(
        db,
        user_id=str(current_user.id),
        action="update_farm",
        resource="farm",
        resource_id=str(farm.id),
        request=request,
        details={"changes": updates},
    )

    return _farm_to_out(farm)


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una finca. Accion registrada en audit log."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    if farm.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    farm_name = farm.name
    db.delete(farm)
    db.commit()

    log_event(
        db,
        user_id=str(current_user.id),
        action="delete_farm",
        resource="farm",
        resource_id=str(farm_id),
        request=request,
        details={"name": farm_name},
    )

    return None
