@echo off
REM ====================================================================
REM  SEMBRARIA — Setup del Frontend
REM  npm install en la carpeta frontend.
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Setup del Frontend
echo ============================================
echo.

REM Detectar Node
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado. Descargalo desde nodejs.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js: %NODE_VERSION%
echo.

cd /d "%~dp0..\apps\web"

REM Copiar .env.example a .env si no existe
if not exist ".env" (
    if exist ".env.example" (
        echo [1/3] Creando .env desde .env.example...
        copy ".env.example" ".env" >nul
    )
) else (
    echo [1/3] .env ya existe
)

echo [2/3] Instalando dependencias (esto puede tardar 1-2 minutos)...
call npm install --silent
if errorlevel 1 (
    echo [ERROR] Fallo en npm install
    pause
    exit /b 1
)

echo [3/3] Verificando instalacion...
if not exist "node_modules" (
    echo [ERROR] node_modules no se creo
    pause
    exit /b 1
)

echo.
echo ============================================
echo  [OK] Frontend listo!
echo ============================================
echo.
echo   Para iniciar: scripts\start-frontend.bat
echo.
endlocal
pause
