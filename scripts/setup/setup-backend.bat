@echo off
REM ====================================================================
REM  SEMBRARIA — Setup del Backend
REM  Crea venv, instala requirements.
REM ====================================================================
setlocal enabledelayedexpansion

echo.
echo ============================================
echo  SembrarIA — Setup del Backend
echo ============================================
echo.

cd /d "%~dp0..\apps\api"

REM Detectar Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado. Instala Python 3.11+ desde python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PY_VERSION=%%i
echo [OK] Python detectado: %PY_VERSION%
echo.

REM Crear venv si no existe
if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear venv
        pause
        exit /b 1
    )
) else (
    echo [1/3] venv ya existe, reutilizando...
)

REM Activar venv
echo [2/3] Activando venv...
call venv\Scripts\activate.bat

REM Actualizar pip
echo [3/3] Instalando dependencias (esto puede tardar 2-3 minutos)...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Fallo en pip install
    pause
    exit /b 1
)

echo.
echo ============================================
echo  [OK] Backend listo!
echo ============================================
echo.
echo   Para iniciar: scripts\start-backend.bat
echo.
endlocal
pause
