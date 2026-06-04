@echo off
REM ====================================================================
REM  SEMBRARIA — Genera los 6 GeoTIFFs sinteticos
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Generando rasters sinteticos
echo ============================================
echo.

cd /d "%~dp0..\apps\api"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv no existe. Ejecuta scripts\setup\setup-backend.bat primero.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python "%~dp0generate_synthetic_rasters.py"

echo.
echo [OK] Rasters generados en data\inputs\
echo.
endlocal
pause
