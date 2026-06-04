#!/bin/bash
# ====================================================================
#  SEMBRARIA — Tests del Backend (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/apps/api"

cd "$BACKEND_DIR"

if [ ! -f "venv/bin/python" ]; then
    echo "[ERROR] venv no existe. Ejecuta bash scripts/setup-backend.sh primero."
    exit 1
fi

source venv/bin/activate
python -m pytest tests/ -v
