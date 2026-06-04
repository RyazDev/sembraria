#!/bin/bash
# ====================================================================
#  SEMBRARIA — Inicia el Frontend (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$ROOT_DIR/apps/web"

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "[ERROR] node_modules no existe. Ejecuta bash scripts/setup-frontend.sh primero."
    exit 1
fi

echo ""
echo "============================================"
echo "  SembrarIA — Iniciando Frontend"
echo "  http://localhost:5173"
echo "============================================"
echo ""

npm run dev
