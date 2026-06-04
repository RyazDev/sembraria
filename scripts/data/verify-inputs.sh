#!/bin/bash
# ====================================================================
#  SEMBRARIA — Verifica que los 6 GeoTIFFs existan (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
INPUTS_DIR="$ROOT_DIR/data/inputs"

echo ""
echo "============================================"
echo "  SembrarIA — Verificando rasters"
echo "============================================"
echo ""

MISSING=0
FOUND=0

for f in aptitud_CACAO.tif aptitud_PLATANO.tif aptitud_YUCA.tif clasificacion_5clases.tif sintesis_mejor_cultivo.tif stack_54features.tif; do
    if [ -f "$INPUTS_DIR/$f" ]; then
        SIZE=$(stat -c%s "$INPUTS_DIR/$f" 2>/dev/null || stat -f%z "$INPUTS_DIR/$f")
        echo "  [OK] $f ($SIZE bytes)"
        FOUND=$((FOUND+1))
    else
        echo "  [FALTA] $f"
        MISSING=$((MISSING+1))
    fi
done

echo ""
echo "Encontrados: $FOUND/6"
echo "Faltantes: $MISSING/6"
echo ""

if [ $MISSING -gt 0 ]; then
    echo "Para generar los faltantes: bash scripts/generate-data.sh"
    exit 1
fi

echo "[OK] Todos los rasters presentes."
echo ""
