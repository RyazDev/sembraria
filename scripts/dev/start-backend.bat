@echo off
REM ====================================================================
REM  SEMBRARIA — Inicia el Backend (FastAPI + Uvicorn)
REM  Puerto: 8000
REM ====================================================================
setlocal

cd /d "%~dp0..\apps\api"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv no existe. Ejecuta scripts\setup-backend.bat primero.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  SembrarIA — Iniciando Backend
echo  http://localhost:8000
echo  http://localhost:8000/docs (Swagger)
echo ============================================
echo.

call venv\Scripts\activate.bat
python -m uvicorn sembraria.main:app --reload --host 0.0.0.0 --port 8000

endlocal
