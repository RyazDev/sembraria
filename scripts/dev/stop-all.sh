#!/bin/bash
# ====================================================================
#  SEMBRARIA — Detener todos los servicios (Linux/Mac/WSL)
# ====================================================================

echo ""
echo "============================================"
echo "  SembrarIA — Deteniendo servicios"
echo "============================================"
echo ""

# Backend puerto 8000
if lsof -i :8000 &>/dev/null; then
    echo "[1/2] Deteniendo backend (puerto 8000)..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
fi

# Frontend puerto 5173
if lsof -i :5173 &>/dev/null; then
    echo "[2/2] Deteniendo frontend (puerto 5173)..."
    lsof -ti :5173 | xargs kill -9 2>/dev/null
fi

# Backup: matar uvicorn
pkill -f "uvicorn sembraria.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo ""
echo "[OK] Servicios detenidos."
echo ""
