# data/inputs/

Aqui van los 6 GeoTIFFs requeridos por SembrarIA.

## Archivos esperados

| Archivo | Descripcion | Origen |
|---------|-------------|--------|
| `aptitud_CACAO.tif` | Raster binario 0/1 - aptitud para cacao | Generar con `scripts/generate-data.bat` o E8 del pipeline |
| `aptitud_PLATANO.tif` | Raster binario 0/1 - aptitud para platano | Generar o E8 |
| `aptitud_YUCA.tif` | Raster binario 0/1 - aptitud para yuca | Generar o E8 |
| `clasificacion_5clases.tif` | Raster 0-4: pasto, bosque, cultivo, agua, urbano | E7 del pipeline |
| `sintesis_mejor_cultivo.tif` | Raster 1-6: cafe, cacao, caucho, platano, yuca, maiz | E8 del pipeline |
| `stack_54features.tif` | 54 bandas para validacion (NDVI, SAR, DEM, etc) | E6 del pipeline |

## Para generar datos sinteticos (demo)

```bash
# Windows
scripts\generate-data.bat

# Linux/Mac
bash scripts/generate-data.sh
```

## Para datos reales del pipeline E3-E8

Copia los 6 archivos GeoTIFF de tu pipeline cientifico (SNAP, QGIS, Python)
a esta carpeta. Deben cumplir:

- CRS: `EPSG:4326`
- Resolucion: 30m (produccion) o 500m (demo sintetico)
- Formato: GeoTIFF
- Compresion: LZW
- Bbox: aproximadamente `[-76.3, -0.7, -73.6, 2.3]` (Caqueta, Colombia)

## Verificar

```bash
# Windows
scripts\verify-inputs.bat

# Linux/Mac
bash scripts/verify-inputs.sh
```
