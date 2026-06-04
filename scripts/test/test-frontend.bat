@echo off
REM ====================================================================
REM  SEMBRARIA — Tests del Frontend
REM ====================================================================
setlocal

cd /d "%~dp0..\apps\web"

if not exist "node_modules" (
    echo [ERROR] node_modules no existe. Ejecuta scripts\setup-frontend.bat primero.
    pause
    exit /b 1
)

call npm test

endlocal
pause
