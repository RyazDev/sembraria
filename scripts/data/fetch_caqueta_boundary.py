#!/usr/bin/env python
"""
SembrarIA - Descarga el poligono oficial del departamento de Caqueta
desde el DANE (DanE - Datos Abiertos Colombia) y lo guarda como
migration SQL.

Fuentes intentadas (en orden):
  1. DANE MGN - Marco Geoestadistico Nacional (GeoJSON oficial)
  2. IGAC - Instituto Geografico Agustin Codazzi
  3. Humanitarian Data Exchange (HDX) - fallback

Uso:
    # Solo descargar a un archivo (sin tocar la DB)
    python scripts/data/fetch_caqueta_boundary.py --output data/inputs/caqueta_dane.geojson

    # Descargar y generar una migration SQL lista para ejecutar
    python scripts/data/fetch_caqueta_boundary.py --output-migration config/db/09_caqueta_dane.sql

    # Especificar el DIVIPOLA del departamento (Caqueta = 18)
    python scripts/data/fetch_caqueta_boundary.py --divipola 18

Si la descarga falla (sin internet, DANE caido), el script sale con
codigo 1 y deja el bbox actual en su lugar.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


# Fuentes alternativas (URLs probables a 2024-2026; pueden cambiar).
SOURCE_URLS = [
    "https://geoportal.dane.gov.cn/magns/api/departments/MGN_Departamento_{divipola}.geojson",
    "https://datosabiertos.esri.co/datasets/esri-colombia::mgn-departamento-{divipola}/api",
    "https://data.humdata.org/dataset/colombia-administrative-boundaries",
]


def download_caqueta(divipola: str, timeout: int = 30) -> dict:
    """Intenta descargar el GeoJSON del DANE. Devuelve dict con el GeoJSON."""
    errors = []
    for url_template in SOURCE_URLS:
        url = url_template.format(divipola=divipola)
        try:
            print(f"Probando: {url}")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SembrarIA/1.0 (+https://sembriaia.udla.edu.co)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read())
                    return {"source_url": url, "data": data}
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            errors.append(f"  - {url}: {e}")
            continue
    raise RuntimeError(
        "No se pudo descargar el poligono desde ninguna fuente:\n"
        + "\n".join(errors)
    )


def geojson_to_multipolygon_wkt(geojson: dict) -> str:
    """Convierte un GeoJSON de tipo Polygon o MultiPolygon a WKT MULTIPOLYGON."""
    if geojson["type"] == "Polygon":
        rings = geojson["coordinates"]
        rings_str = ", ".join(
            "(" + ", ".join(f"{x} {y}" for x, y in ring) + ")" for ring in rings
        )
        return f"MULTIPOLYGON({rings_str})"
    elif geojson["type"] == "MultiPolygon":
        polys_str = ", ".join(
            "("
            + ", ".join(
                "(" + ", ".join(f"{x} {y}" for x, y in ring) + ")" for ring in poly
            )
            + ")"
            for poly in geojson["coordinates"]
        )
        return f"MULTIPOLYGON({polys_str})"
    else:
        raise ValueError(f"Tipo GeoJSON no soportado: {geojson['type']}")


def generate_migration(wkt: str, source_url: str, divipola: str) -> str:
    """Genera una migration SQL lista para ejecutar."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"""-- ====================================================================
-- SembrarIA — 09 Poligono oficial del departamento de Caqueta (DANE)
-- Generado automaticamente por scripts/data/fetch_caqueta_boundary.py
-- Fecha: {now}
-- DIVIPOLA: {divipola}
-- Fuente: {source_url}
-- ====================================================================

UPDATE caqueta_boundary
SET
    geom = ST_GeomFromText('{wkt}', 4326),
    data_provenance = 'dane',
    source_url = '{source_url}',
    fetched_at = NOW(),
    notes = 'Poligono oficial descargado del DANE/IGAC el {now}'
WHERE nombre = 'Caqueta';

-- Si no existe, lo inserta (caso de primera instalacion sin la fila)
INSERT INTO caqueta_boundary (nombre, geom, data_provenance, source_url, fetched_at, notes)
SELECT 'Caqueta', ST_GeomFromText('{wkt}', 4326), 'dane', '{source_url}', NOW(),
       'Poligono oficial DANE insertado por primera vez'
WHERE NOT EXISTS (SELECT 1 FROM caqueta_boundary WHERE nombre = 'Caqueta');

SELECT 'Caqueta boundary actualizado: ' || data_provenance AS status
FROM caqueta_boundary
LIMIT 1;
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga el poligono oficial de Caqueta del DANE"
    )
    parser.add_argument(
        "--divipola",
        default="18",
        help="Codigo DIVIPOLA del departamento (Caqueta = 18)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Guardar el GeoJSON crudo en este path",
    )
    parser.add_argument(
        "--output-migration",
        type=Path,
        help="Generar una migration SQL en este path",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout HTTP en segundos",
    )
    args = parser.parse_args()

    print(f"Descargando poligono de Caqueta (DIVIPOLA={args.divipola})...")
    try:
        result = download_caqueta(args.divipola, args.timeout)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    source_url = result["source_url"]
    data = result["data"]
    print(f"OK: descargado desde {source_url}")
    print(f"   tipo: {data.get('type')}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"   guardado en: {args.output}")

    if args.output_migration:
        try:
            wkt = geojson_to_multipolygon_wkt(data)
        except (KeyError, ValueError) as e:
            print(f"ERROR convirtiendo GeoJSON: {e}", file=sys.stderr)
            return 1
        sql = generate_migration(wkt, source_url, args.divipola)
        args.output_migration.parent.mkdir(parents=True, exist_ok=True)
        args.output_migration.write_text(sql, encoding="utf-8")
        print(f"   migration SQL guardada en: {args.output_migration}")
        print(f"   WKT length: {len(wkt)} chars")

    print()
    print("Proximos pasos:")
    print("  1. Revisar la migration generada")
    print("  2. Ejecutarla con: psql -U postgres -d sembraria -f <archivo.sql>")
    print("  3. Reiniciar el backend para que la cache LRU recargue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
