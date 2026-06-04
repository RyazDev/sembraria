@echo off
REM ====================================================================
REM  SEMBRARIA — Inicia el Frontend (Vite dev server)
REM  Puerto: 5173
REM ====================================================================
setlocal

cd /d "%~dp0..\apps\web"

if not exist "node_modules" (
    echo [ERROR] node_modules no existe. Ejecuta scripts\setup-frontend.bat primero.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  SembrarIA — Iniciando Frontend
echo  http://localhost:5173
echo ============================================
echo.

call npm run dev

endlocal
