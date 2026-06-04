#!/bin/bash
# ====================================================================
#  SEMBRARIA — Setup de Base de Datos (Linux/Mac/WSL)
# ====================================================================

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "============================================"
echo "  SembrarIA — Setup de Base de Datos"
echo "============================================"
echo ""

# Verificar PostGIS
bash "$SCRIPT_DIR/install-postgis.sh"

# Verificar .env
if [ ! -f "$ROOT_DIR/.env" ]; then
    if [ -f "$ROOT_DIR/.env.example" ]; then
        echo "[AVISO] .env no existe. Copiando desde .env.example..."
        cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
        echo "[OK] .env creado."
    else
        echo "[ERROR] No se encuentra .env.example"
        exit 1
    fi
fi

export PGPASSWORD=postgres

echo "[1/3] Eliminando DB 'sembraria' si existe..."
psql -U postgres -c "DROP DATABASE IF EXISTS sembraria;" 2>/dev/null || true

echo "[2/3] Creando DB 'sembraria'..."
psql -U postgres -c "CREATE DATABASE sembraria;"

echo "[3/3] Corriendo scripts init-db/*.sql..."
for sql_file in "$ROOT_DIR"/config/db/*.sql; do
    echo "  Ejecutando $(basename "$sql_file")..."
    psql -U postgres -d sembraria -f "$sql_file" -q
done

echo ""
echo "============================================"
echo "  [OK] Base de datos 'sembraria' lista!"
echo "============================================"
echo ""
psql -U postgres -d sembraria -c "\dt"
echo ""
echo "  Siguiente paso: bash scripts/setup-backend.sh"
echo ""
