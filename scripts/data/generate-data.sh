#!/bin/bash
# ====================================================================
#  SEMBRARIA — Genera los 6 GeoTIFFs sinteticos (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "============================================"
echo "  SembrarIA — Generando rasters sinteticos"
echo "============================================"
echo ""

cd "$ROOT_DIR/apps/api"

if [ ! -f "venv/bin/python" ]; then
    echo "[ERROR] venv no existe. Ejecuta bash scripts/setup-backend.sh primero."
    exit 1
fi

source venv/bin/activate
python "$SCRIPT_DIR/generate_synthetic_rasters.py"

echo ""
echo "[OK] Rasters generados en data/inputs/"
echo ""
