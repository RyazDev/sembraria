@echo off
REM ====================================================================
REM  SEMBRARIA — Tests del Backend
REM ====================================================================
setlocal

cd /d "%~dp0..\apps\api"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv no existe. Ejecuta scripts\setup-backend.bat primero.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m pytest tests/ -v

endlocal
pause
