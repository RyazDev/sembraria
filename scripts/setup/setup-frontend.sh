#!/bin/bash
# ====================================================================
#  SEMBRARIA — Setup del Frontend (Linux/Mac/WSL)
# ====================================================================

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$ROOT_DIR/apps/web"

echo ""
echo "============================================"
echo "  SembrarIA — Setup del Frontend"
echo "============================================"
echo ""

# Detectar Node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js no esta instalado."
    echo "  https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "[OK] Node.js: $NODE_VERSION"
echo ""

cd "$FRONTEND_DIR"

# Copiar .env
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[1/3] Creando .env desde .env.example..."
    cp .env.example .env
else
    echo "[1/3] .env ya existe"
fi

echo "[2/3] Instalando dependencias..."
npm install --silent

echo "[3/3] Verificando instalacion..."
if [ ! -d "node_modules" ]; then
    echo "[ERROR] node_modules no se creo"
    exit 1
fi

echo ""
echo "============================================"
echo "  [OK] Frontend listo!"
echo "============================================"
echo ""
echo "  Para iniciar: bash scripts/start-frontend.sh"
echo ""
