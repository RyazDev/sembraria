"""
Catalog endpoint: expone el catalogo de cultivos y configuracion geofence.
Usado por el frontend para construir formularios dinamicamente.
"""
from fastapi import APIRouter

from sembraria.config import get_crops_config, get_geofence_config, get_raster_config

router = APIRouter()


@router.get("/catalog/crops")
async def get_crops():
    """Devuelve el catalogo de cultivos disponibles."""
    config = get_crops_config()
    return {"crops": config.get("crops", []), "synthesis": config.get("synthesis")}


@router.get("/catalog/geofence")
async def get_geofence():
    """Devuelve la configuracion del geofence de Caqueta."""
    return get_geofence_config()


@router.get("/catalog/raster")
async def get_raster():
    """Devuelve parametros de raster."""
    return get_raster_config()


@router.get("/catalog/all")
async def get_all_catalogs():
    """Devuelve todos los catalogos en una sola llamada."""
    return {
        "crops": get_crops_config(),
        "geofence": get_geofence_config(),
        "raster": get_raster_config(),
    }
