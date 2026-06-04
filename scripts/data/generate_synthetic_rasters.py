"""
SembrarIA - Synthetic Raster Generator.
Genera los 6 GeoTIFFs sinteticos para Caqueta, Colombia.
Reproducible (seed=42) y liviano (resolucion 500m).

Ejecutar: python scripts/data/generate_synthetic_rasters.py
"""
import sys
from pathlib import Path
import yaml

import numpy as np
import rasterio
from rasterio.transform import from_bounds

# Raiz del proyecto: scripts/data/ -> scripts/ -> raiz
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def load_config():
    """Carga configuracion desde YAML."""
    config_dir = PROJECT_ROOT / "config" / "catalog"
    with open(config_dir / "geofence.yaml", "r", encoding="utf-8") as f:
        geofence = yaml.safe_load(f)["caqueta"]
    with open(config_dir / "raster.yaml", "r", encoding="utf-8") as f:
        raster = yaml.safe_load(f)["raster"]
    with open(config_dir / "crops.yaml", "r", encoding="utf-8") as f:
        crops = yaml.safe_load(f)
    return geofence, raster, crops


def make_transform(minx, miny, maxx, maxy, width, height):
    """Crea el Affine transform para el raster."""
    return from_bounds(minx, miny, maxx, maxy, width, height)


def make_simulated_elevation(width, height):
    """
    Genera un patron de elevacion simulado para Caqueta.
    - Valles al oeste (cercanos a Florencia)
    - Montanas al este (Andes)
    Valores normalizados [0, 1].
    """
    # Gradiente oeste-este
    gradient = np.linspace(0, 1, width)
    elevation_2d = np.tile(gradient, (height, 1))
    # Ruido suave
    noise = np.random.random((height, width)) * 0.3
    elevation = elevation_2d + noise
    return np.clip(elevation, 0, 1)


def make_simulated_precipitation(width, height, elevation):
    """Precipitacion inversa a elevacion (mas lluvia en valles)."""
    return 1.0 - elevation * 0.7 + np.random.random((height, width)) * 0.2


def make_binary_aptitud(filename, transform, crs, width, height, threshold_fn, label=""):
    """
    Genera un raster binario (0=no apto, 1=apto) segun threshold_fn(elevation, precip, random).
    """
    elevation = make_simulated_elevation(width, height)
    precip = make_simulated_precipitation(width, height, elevation)
    random_field = np.random.random((height, width))

    # Aplicar threshold
    mask = threshold_fn(elevation, precip, random_field)
    data = mask.astype(np.uint8)

    write_geotiff(filename, data, transform, crs, nodata=255, label=label)
    return data


def write_geotiff(filename, data, transform, crs, nodata=None, label=""):
    """Escribe un array numpy como GeoTIFF."""
    filepath = PROJECT_ROOT / "data" / "inputs" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if data.ndim == 2:
        count = 1
        height, width = data.shape
    elif data.ndim == 3:
        count = data.shape[0]
        height, width = data.shape[1], data.shape[2]
    else:
        raise ValueError(f"Data debe ser 2D o 3D, got {data.ndim}D")

    with rasterio.open(
        filepath,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=count,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
        nodata=nodata,
        compress="lzw",
        tiled=True,
        blockxsize=512,
        blockysize=512,
    ) as dst:
        if data.ndim == 2:
            dst.write(data, 1)
            dst.set_band_description(1, label or filename)
        else:
            for i in range(count):
                dst.write(data[i], i + 1)

    size_kb = filepath.stat().st_size / 1024
    print(f"  [OK] {filename} ({data.shape}, {size_kb:.1f} KB)")


def generate_cacao_aptitud(width, height, transform, crs):
    """Cacao: valles bajos (<0.4), precipitacion alta."""
    def threshold(e, p, r):
        return ((e < 0.4) & (p > 0.5) & (r > 0.3)).astype(np.uint8)
    return make_binary_aptitud("aptitud_CACAO.tif", transform, crs, width, height, threshold, "Aptitud Cacao")


def generate_platano_aptitud(width, height, transform, crs):
    """Platano: zonas medias (0.3 < e < 0.7), humedad balanceada."""
    def threshold(e, p, r):
        return ((e > 0.3) & (e < 0.7) & (p > 0.4) & (r > 0.3)).astype(np.uint8)
    return make_binary_aptitud("aptitud_PLATANO.tif", transform, crs, width, height, threshold, "Aptitud Platano")


def generate_yuca_aptitud(width, height, transform, crs):
    """Yuca: zonas variadas (tolerante), pero mejor en medias."""
    def threshold(e, p, r):
        return ((e > 0.2) & (e < 0.8) & (r > 0.4)).astype(np.uint8)
    return make_binary_aptitud("aptitud_YUCA.tif", transform, crs, width, height, threshold, "Aptitud Yuca")


def generate_clasificacion(width, height, transform, crs):
    """Clasificacion 5-clase: 0=pasto, 1=bosque, 2=cultivo, 3=agua, 4=urbano."""
    # Distribucion realista: ~70% pasto, ~20% bosque, ~7% cultivo, ~2% agua, ~1% urbano
    probs = [0.70, 0.20, 0.07, 0.02, 0.01]
    classes = np.random.choice(5, size=(height, width), p=probs)
    # Bosques mas probables en zonas altas (este)
    gradient = np.linspace(0, 1, width)
    elevation_bias = np.tile(gradient, (height, 1))
    # Donde elevacion > 0.6, forzar bosque
    forest_mask = (elevation_bias > 0.6) & (np.random.random((height, width)) > 0.3)
    classes[forest_mask] = 1
    # Donde elevacion < 0.2, mas agua
    water_mask = (elevation_bias < 0.2) & (np.random.random((height, width)) > 0.85)
    classes[water_mask] = 3
    data = classes.astype(np.uint8)
    write_geotiff("clasificacion_5clases.tif", data, transform, crs, nodata=255, label="Clasificacion 5-clase")
    return data


def generate_sintesis(width, height, transform, crs):
    """Sintesis de mejor cultivo: 1=Cafe, 2=Cacao, 3=Caucho, 4=Platano, 5=Yuca, 6=Maiz."""
    probs = [0.15, 0.25, 0.10, 0.20, 0.20, 0.10]  # distribucion realista
    synth = np.random.choice([1, 2, 3, 4, 5, 6], size=(height, width), p=probs)
    # Cacao y cafe en zonas bajas, platano y yuca en medias, caucho en altas
    gradient = np.linspace(0, 1, width)
    elev_2d = np.tile(gradient, (height, 1))
    # Oeste (bajo) -> Cafe, Cacao; Centro -> Platano, Yuca; Este (alto) -> Caucho
    low_mask = (elev_2d < 0.33) & (np.random.random((height, width)) > 0.5)
    synth[low_mask] = np.random.choice([1, 2], size=int(low_mask.sum()))  # Cafe, Cacao
    mid_mask = (elev_2d >= 0.33) & (elev_2d < 0.66) & (np.random.random((height, width)) > 0.5)
    synth[mid_mask] = np.random.choice([4, 5], size=int(mid_mask.sum()))  # Platano, Yuca
    high_mask = (elev_2d >= 0.66) & (np.random.random((height, width)) > 0.6)
    synth[high_mask] = np.random.choice([3, 6], size=int(high_mask.sum()))  # Caucho, Maiz
    data = synth.astype(np.uint8)
    write_geotiff("sintesis_mejor_cultivo.tif", data, transform, crs, nodata=255, label="Sintesis Mejor Cultivo")
    return data


def generate_stack_54features(width, height, transform, crs):
    """Stack de 54 features para validacion E3-E8 (no se usa en extraccion zonal)."""
    print(f"  Generando 54 bandas (esto puede tardar ~30 segundos)...")
    np.random.seed(42)
    elevation = make_simulated_elevation(width, height)
    precip = make_simulated_precipitation(width, height, elevation)

    # 54 bandas distribuidas asi:
    # 0-9: Indices espectrales (NDVI, EVI, NDWI, SAVI, etc) - 10
    # 10-19: Sentinel-2 bandas (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12) - 10
    # 20-25: Sentinel-1 SAR (VV, VH, ratio, etc) - 6
    # 26-30: DEM derivados (slope, aspect, TWI, TPI, curvature) - 5
    # 31-39: Fenologia (amplitud, integral, fechas min/max NDVI) - 9
    # 40-45: ERA5 (temp, precipitacion, humedad) - 6
    # 46-49: MODIS LST - 4
    # 50-53: WorldCover / otras - 4

    stack = np.zeros((54, height, width), dtype=np.float32)
    band_names = []

    for i in range(54):
        if i < 10:  # Indices espectrales
            base = np.random.random((height, width))
            stack[i] = base * 0.7 + elevation * 0.3
            band_names.append(f"INDEX_{i:02d}")
        elif i < 20:  # Sentinel-2
            base = np.random.random((height, width))
            stack[i] = base * 0.5 + precip * 0.5
            band_names.append(f"S2_B{i-9:02d}")
        elif i < 26:  # Sentinel-1 SAR
            base = np.random.random((height, width))
            stack[i] = base * 0.8 + np.random.normal(0, 0.1, (height, width))
            band_names.append(f"S1_{i-19:02d}")
        elif i < 31:  # DEM
            stack[i] = elevation * np.random.uniform(0.5, 1.5)
            band_names.append(f"DEM_{i-25:02d}")
        elif i < 40:  # Fenologia
            base = np.sin(np.linspace(0, 2 * np.pi, width))
            base_2d = np.tile(base, (height, 1))
            stack[i] = base_2d * 0.6 + np.random.random((height, width)) * 0.4
            band_names.append(f"PHENO_{i-30:02d}")
        elif i < 46:  # ERA5
            stack[i] = precip * 0.5 + np.random.random((height, width)) * 0.5
            band_names.append(f"ERA5_{i-39:02d}")
        elif i < 50:  # MODIS LST
            stack[i] = (1 - elevation) * 0.4 + np.random.random((height, width)) * 0.3
            band_names.append(f"MODIS_{i-45:02d}")
        else:  # Otros
            stack[i] = np.random.random((height, width))
            band_names.append(f"OTHER_{i-49:02d}")

    write_geotiff("stack_54features.tif", stack, transform, crs, nodata=-9999, label="Stack 54 features")


def main():
    """Genera todos los rasters sinteticos."""
    print("=" * 60)
    print("  SEMBRARIA — Generador de Rasters Sinteticos")
    print("=" * 60)

    np.random.seed(42)  # Reproducibilidad

    geofence, raster_cfg, crops_cfg = load_config()
    bbox = geofence["bbox"]
    minx, miny, maxx, maxy = bbox
    pixel_m = raster_cfg["demo_pixel_size_m"]

    # Aproximacion: 1 grado ~ 111 km en latitud
    width_deg = maxx - minx
    height_deg = maxy - miny
    # Calcular pixeles (resolucion 500m)
    width = int(width_deg * 111000 / pixel_m)
    height = int(height_deg * 111000 / pixel_m)

    # Cap para que no sea muy pesado
    width = min(width, 600)
    height = min(height, 400)

    print(f"  Bbox Caqueta: {bbox}")
    print(f"  Resolucion: {pixel_m}m")
    print(f"  Dimensiones: {width} x {height} pixeles")
    print()

    transform = make_transform(minx, miny, maxx, maxy, width, height)
    crs = "EPSG:4326"

    print("[1/6] Generando rasters de aptitud...")
    generate_cacao_aptitud(width, height, transform, crs)
    generate_platano_aptitud(width, height, transform, crs)
    generate_yuca_aptitud(width, height, transform, crs)

    print("[2/6] Generando clasificacion 5-clase...")
    generate_clasificacion(width, height, transform, crs)

    print("[3/6] Generando sintesis mejor cultivo...")
    generate_sintesis(width, height, transform, crs)

    print("[4/6] Generando stack de 54 features...")
    generate_stack_54features(width, height, transform, crs)

    print()
    print("=" * 60)
    print(f"  [OK] 6 archivos generados en data/inputs/")
    print("=" * 60)
    print()
    print("  Siguiente paso: scripts/setup-db.bat para inicializar la DB")


if __name__ == "__main__":
    main()
