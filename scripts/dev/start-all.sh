#!/bin/bash
# ====================================================================
#  SEMBRARIA — Inicia Backend y Frontend en paralelo (Linux/Mac/WSL)
# ====================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "============================================"
echo "  SembrarIA — Iniciando todo"
echo "============================================"
echo ""

# Backend en background
bash "$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

sleep 3

# Frontend en background
bash "$SCRIPT_DIR/start-frontend.sh" &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "  Backend:  http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Para detener: bash scripts/stop-all.sh"
echo ""

# Esperar a que cualquiera termine
wait
