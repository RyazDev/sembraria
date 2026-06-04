@echo off
REM ====================================================================
REM  SEMBRARIA — Inicia Backend y Frontend en paralelo (2 ventanas)
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Iniciando todo (Backend + Frontend)
echo ============================================
echo.

REM Backend en nueva ventana
start "SembrarIA Backend" cmd /k "call "%~dp0start-backend.bat""

REM Esperar 3 segundos para que el backend arranque primero
timeout /t 3 /nobreak >nul

REM Frontend en nueva ventana
start "SembrarIA Frontend" cmd /k "call "%~dp0start-frontend.bat""

echo [OK] Ambos servicios iniciados en ventanas separadas.
echo.
echo   Backend:  http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo.
echo   Para detener: scripts\stop-all.bat
echo.
pause
endlocal
