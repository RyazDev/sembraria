@echo off
REM ====================================================================
REM  SEMBRARIA — Detener todos los servicios
REM  Mata procesos en puertos 8000 (backend) y 5173 (frontend).
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Deteniendo servicios
echo ============================================
echo.

REM Backend (puerto 8000)
echo [1/2] Deteniendo backend (puerto 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo   Matando PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Frontend (puerto 5173)
echo [2/2] Deteniendo frontend (puerto 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo   Matando PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Backup: matar procesos de node y python con nombres comunes
taskkill /F /IM "uvicorn.exe" >nul 2>&1
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq SembrarIA*" >nul 2>&1

echo.
echo [OK] Servicios detenidos.
echo.
endlocal
pause
