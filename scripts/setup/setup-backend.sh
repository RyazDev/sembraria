#!/bin/bash
# ====================================================================
#  SEMBRARIA — Setup del Backend (Linux/Mac/WSL)
# ====================================================================

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/apps/api"

echo ""
echo "============================================"
echo "  SembrarIA — Setup del Backend"
echo "============================================"
echo ""

# Detectar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no esta instalado."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-dev"
    echo "  Mac: brew install python"
    exit 1
fi

PY_VERSION=$(python3 --version)
echo "[OK] $PY_VERSION"
echo ""

cd "$BACKEND_DIR"

# Crear venv
if [ ! -d "venv" ]; then
    echo "[1/3] Creando entorno virtual..."
    python3 -m venv venv
else
    echo "[1/3] venv ya existe, reutilizando..."
fi

echo "[2/3] Activando venv..."
source venv/bin/activate

echo "[3/3] Instalando dependencias..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""
echo "============================================"
echo "  [OK] Backend listo!"
echo "============================================"
echo ""
echo "  Para iniciar: bash scripts/start-backend.sh"
echo ""
