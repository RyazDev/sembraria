#!/bin/bash
# ====================================================================
#  SEMBRARIA — Inicia el Backend (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/apps/api"

cd "$BACKEND_DIR"

if [ ! -f "venv/bin/python" ]; then
    echo "[ERROR] venv no existe. Ejecuta bash scripts/setup-backend.sh primero."
    exit 1
fi

echo ""
echo "============================================"
echo "  SembrarIA — Iniciando Backend"
echo "  http://localhost:8000"
echo "  http://localhost:8000/docs (Swagger)"
echo "============================================"
echo ""

source venv/bin/activate
python -m uvicorn sembraria.main:app --reload --host 0.0.0.0 --port 8000
