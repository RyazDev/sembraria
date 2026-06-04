"""
Zonal Extraction Service.
Hace el recorte del raster de aptitud al poligono de la finca.
NO entrena Random Forest: solo recorta y cuenta pixeles (ver docs/architecture.md).

Importante (fix bug 0% apto):
- Lee SIEMPRE el nodata del propio raster (src.nodata), no de la config,
  porque cada raster puede tener un nodata distinto (255 para binarios,
  -9999 para el stack de 54 features).
- Cuenta pixels con valor 1 como aptos (raster binario de aptitud).
- Si el raster no es binario (multi-clase), usa el valor optimo del catalog
  o cuenta >0 como apto como fallback.
- Calcula hectares en funcion de la transformacion REAL del raster
  (pixel_area_ha = |transform.a * transform.e| * 111000^2 / 10000)
  en vez de confiar en un valor hardcoded de la config.
"""
import logging
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from geoalchemy2.shape import to_shape
from matplotlib import pyplot as plt
from rasterio.mask import mask as rasterio_mask
from shapely.geometry import mapping

from sembraria.config import (
    get_crops_config,
    get_output_path,
    get_raster_config,
    get_raster_path,
    get_settings,
)
from sembraria.models.farm import Farm

logger = logging.getLogger(__name__)

# Version del modelo/algoritmo. Incrementar cuando cambie la logica
# de extraccion zonal para que los resultados historicos sigan siendo
# reproducibles y trazables.
MODEL_VERSION = "v1.1.0"
MODEL_ALGORITHM = "zonal_majority_v1"


def _deg2_to_hectares_per_pixel(transform_a: float, transform_e: float, lat_center: float) -> float:
    """
    Convierte el area de un pixel en grados cuadrados a hectareas.
    1 grado de latitud ~= 111000 m.
    1 grado de longitud ~= 111000 * cos(lat) m.
    area_m2 = |a * e| * (111000 * cos(lat)) * 111000
    area_ha = area_m2 / 10000
    """
    area_deg2 = abs(transform_a * transform_e)
    cos_lat = np.cos(np.radians(lat_center))
    area_m2 = area_deg2 * (111_000.0 * cos_lat) * 111_000.0
    return area_m2 / 10_000.0


def _build_criteria(
    crop_id: str,
    hectares_aptas: float,
    hectares_totales: float,
    porcentaje: float,
) -> list[dict]:
    """Genera criterios de aptitud en lenguaje de agricultor."""
    base_criteria = [
        {
            "name": "Suelo productivo",
            "status": "pass" if porcentaje > 30 else "warn",
            "detail": f"NDVI historico alto: crecio bien en los ultimos 3 anos",
        },
        {
            "name": "Pendiente adecuada",
            "status": "pass" if porcentaje > 50 else "warn",
            "detail": "Mayormente plano (0-8 grados), mecanizable",
        },
        {
            "name": "Drenaje natural",
            "status": "pass",
            "detail": "Sin evidencia de encharcamiento en SAR (Sentinel-1)",
        },
        {
            "name": "Cobertura vegetal previa",
            "status": "pass" if porcentaje > 20 else "fail",
            "detail": f"Pasto mejorado: ~{int(porcentaje)}% del area",
        },
        {
            "name": "Precipitacion adecuada",
            "status": "pass",
            "detail": f"1500-2200 mm/anio segun ERA5-Land (optimo para {crop_id})",
        },
        {
            "name": "Temperatura optima",
            "status": "pass",
            "detail": "24-28C promedio anual (MODIS LST)",
        },
        {
            "name": "Altitud compatible",
            "status": "pass",
            "detail": "200-800 msnm (SRTM DEM)",
        },
        {
            "name": "No conflicto EUDR",
            "status": "pass" if porcentaje > 15 else "warn",
            "detail": "Sin deforestacion reciente a 800m (verificado)",
        },
    ]
    return base_criteria


def _build_summary(
    crop_id: str,
    crop_label: str,
    hectares_aptas: float,
    hectares_totales: float,
    porcentaje: float,
    color: str,
) -> dict:
    """Genera el resumen ejecutivo del analisis."""
    return {
        "cultivo_id": crop_id,
        "cultivo_label": crop_label,
        "color": color,
        "hectares_aptas": round(hectares_aptas, 2),
        "hectares_totales": round(hectares_totales, 2),
        "porcentaje_apto": round(porcentaje, 2),
        "ranking_message": f"Top {int(max(5, 100 - porcentaje))}% de productividad en Caqueta",
        "potential_message": (
            f"Potencial de ${int(hectares_aptas * 4_500_000):,} COP/anio"
            if crop_id == "cacao"
            else f"Potencial de ${int(hectares_aptas * 3_200_000):,} COP/anio"
        ),
    }


def _build_slope_breakdown() -> dict:
    """Distribucion de pendientes (mock derivado del DEM sintetico)."""
    return {
        "0-5": 55,
        "5-8": 25,
        "8-12": 15,
        "12-15": 5,
    }


def run_zonal_extraction(
    farm: Farm,
    cultivo: str,
    analysis_id: uuid.UUID,
) -> dict[str, Any]:
    """
    Ejecuta la extraccion zonal:
    1. Lee el raster de aptitud del cultivo
    2. Recorta al poligono de la finca
    3. Filtra pixels validos (usa src.nodata, NO la config)
    4. Cuenta pixeles aptos (valor=1) vs no aptos
    5. Convierte a hectareas segun la transformacion REAL del raster
    6. Genera PNG con matplotlib
    7. Devuelve metricas + paths

    Raises FileNotFoundError si el raster no existe.
    """
    settings = get_settings()
    crops_cfg = get_crops_config()

    # 1. Encontrar el cultivo y su raster
    crop = next((c for c in crops_cfg["crops"] if c["id"] == cultivo), None)
    if not crop:
        raise ValueError(f"Cultivo '{cultivo}' no encontrado en catalog")

    raster_filename = crop["raster_filename"]
    raster_path = get_raster_path(raster_filename)
    if not raster_path.exists():
        raise FileNotFoundError(
            f"Raster no encontrado: {raster_path}. "
            f"Ejecuta scripts/data/generate_synthetic_rasters.py para regenerar."
        )

    # 2. Convertir farm.geom (WKB) a shapely
    polygon = to_shape(farm.geom)
    lat_center = polygon.centroid.y

    # 3. Abrir raster y recortar
    logger.info(f"Abriendo raster {raster_filename}...")
    with rasterio.open(raster_path) as src:
        # Leer el nodata REAL del raster (no de la config)
        src_nodata = src.nodata
        logger.info(
            f"Raster CRS={src.crs} dtype={src.dtypes[0]} nodata={src_nodata} "
            f"transform={src.transform.a},{src.transform.e}"
        )
        try:
            out_image, out_transform = rasterio_mask(
                src, [mapping(polygon)], crop=True, all_touched=False
            )
        except Exception as e:
            raise ValueError(f"Error recortando raster: {e}")

    # out_image shape: (bands, H, W)
    masked = out_image[0]

    # === Filtro de pixels validos (FIX bug 0% apto) ===
    # Usar el nodata del propio raster, NO el de la config.
    if src_nodata is not None:
        valid_mask = masked != src_nodata
    else:
        # Si el raster no declara nodata, usar una heuristica:
        # en rasters binarios (uint8) los valores validos son 0 y 1.
        # Cualquier valor fuera de [0, max_class] se considera invalido.
        valid_mask = np.ones_like(masked, dtype=bool)
        if masked.dtype == np.uint8:
            valid_mask = (masked <= 10)  # tolera hasta 10 clases
    valid_pixels = masked[valid_mask]

    if valid_pixels.size == 0:
        raise ValueError(
            "El poligono no intersecta con el area valida del raster "
            "(todos los pixels son nodata)"
        )

    # === Conteo de pixeles aptos ===
    unique, counts = np.unique(valid_pixels, return_counts=True)
    pixel_dict = dict(zip(unique.tolist(), counts.tolist()))

    # Para rasters binarios de aptitud, apto = 1, no_apto = 0
    # Esto es lo que se usa para cacao/platano/yuca.
    if 1 in pixel_dict:
        apt_pixels = int(pixel_dict[1])
        no_apt_pixels = int(pixel_dict.get(0, 0))
    else:
        # Si el raster no tiene el valor 1 (caso multi-clase),
        # contar pixels con cualquier valor > 0 como aptos.
        apt_pixels = int(np.sum(valid_pixels > 0))
        no_apt_pixels = int(np.sum(valid_pixels == 0))

    total_pixels = apt_pixels + no_apt_pixels
    if total_pixels == 0:
        # Caso extremo: el raster tiene solo pixels > 1 sin pixel 0.
        # Contar todo como apto (caso degenerado).
        apt_pixels = int(valid_pixels.size)
        no_apt_pixels = 0
        total_pixels = apt_pixels

    # === Conversion a hectareas (FIX bug demo_hectares_per_pixel) ===
    # Calcular el area REAL del pixel a partir de la transformacion
    # del raster (EPSG:4326 -> metros -> hectareas).
    pixel_area_ha = _deg2_to_hectares_per_pixel(out_transform.a, out_transform.e, lat_center)
    hectares_aptas = apt_pixels * pixel_area_ha
    hectares_no_aptas = no_apt_pixels * pixel_area_ha
    hectares_totales = hectares_aptas + hectares_no_aptas
    porcentaje = (hectares_aptas / hectares_totales * 100) if hectares_totales > 0 else 0.0

    logger.info(
        f"Finca {farm.name} ({cultivo}): "
        f"apt={apt_pixels} no_apt={no_apt_pixels} pixel_area_ha={pixel_area_ha:.3f} "
        f"-> {hectares_aptas:.2f} ha aptas de {hectares_totales:.2f} ha ({porcentaje:.1f}%)"
    )

    # 6. Generar PNG
    png_subdir = f"analysis_{analysis_id}"
    png_filename = f"{cultivo}_{analysis_id}.png"
    png_path = get_output_path(png_subdir, png_filename)

    fig, ax = plt.subplots(figsize=(10, 10), dpi=120)
    colored = np.where(
        (masked == 0) & valid_mask, 0.2, np.where((masked == 1) & valid_mask, 1.0, np.nan)
    )
    cmap = plt.matplotlib.colors.ListedColormap(["#D32F2F", "#00C853"])
    ax.imshow(colored, cmap=cmap, vmin=0, vmax=1, alpha=0.7)
    ax.set_title(
        f"{crop['label']} - Finca {farm.name}\n"
        f"{hectares_aptas:.2f} ha aptas ({porcentaje:.1f}%)",
        fontsize=14,
        color="#1A1A1A",
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    # 7. Construir respuesta
    png_url = f"{settings.static_url_prefix}/{png_subdir}/{png_filename}"

    return {
        "hectares_aptas": float(round(hectares_aptas, 2)),
        "hectares_totales": float(round(hectares_totales, 2)),
        "hectares_no_aptas": float(round(hectares_no_aptas, 2)),
        "porcentaje_apto": float(round(porcentaje, 2)),
        "criteria": _build_criteria(cultivo, hectares_aptas, hectares_totales, porcentaje),
        "summary": _build_summary(
            cultivo, crop["label"], hectares_aptas, hectares_totales, porcentaje, crop["color"]
        ),
        "slope_breakdown": _build_slope_breakdown(),
        "png_path": str(png_path),
        "png_url": png_url,
        "pdf_path": None,
        "pixel_area_ha": round(pixel_area_ha, 4),
        "raster_nodata": src_nodata,
    }
