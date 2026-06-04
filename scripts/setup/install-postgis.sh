#!/bin/bash
# ====================================================================
#  SEMBRARIA — Detector de PostGIS (Linux/Mac/WSL)
# ====================================================================

set -e
echo ""
echo "============================================"
echo "  SembrarIA — Detector de PostGIS"
echo "============================================"
echo ""

# Detectar psql
if ! command -v psql &> /dev/null; then
    echo "[ERROR] psql no esta en PATH. Instala PostgreSQL primero."
    echo "  Ubuntu/Debian: sudo apt install postgresql postgis"
    echo "  Mac: brew install postgis"
    echo ""
    exit 1
fi

PG_VERSION=$(psql --version | awk '{print $3}')
echo "[OK] PostgreSQL detectado: $PG_VERSION"
echo ""

# Probar conexion
export PGPASSWORD=postgres
if ! psql -U postgres -c "SELECT 1" >/dev/null 2>&1; then
    echo "[AVISO] No se pudo conectar como 'postgres'. Ajusta el .env"
    echo ""
    exit 1
fi
echo "[OK] Conexion a PostgreSQL exitosa."
echo ""

# Verificar PostGIS
if ! psql -U postgres -tAc "SELECT 1 FROM pg_available_extensions WHERE name='postgis';" | grep -q 1; then
    echo "============================================"
    echo "  [FALTA] PostGIS no esta disponible"
    echo "============================================"
    echo ""
    echo "  Ubuntu/Debian: sudo apt install postgresql-15-postgis-3"
    echo "  Mac: brew install postgis"
    echo ""
    exit 1
fi

echo "[OK] PostGIS esta disponible."
psql -U postgres -tAc "SELECT PostGIS_Version();"
echo ""
echo "============================================"
echo "  Listo! PostGIS esta correctamente instalado."
echo "============================================"
echo ""
