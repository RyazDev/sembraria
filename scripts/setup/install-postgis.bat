@echo off
REM ====================================================================
REM  SEMBRARIA — Detector de PostGIS
REM  Verifica que PostGIS este disponible. Si no, guia la instalacion.
REM ====================================================================
setlocal enabledelayedexpansion

echo.
echo ============================================
echo  SembrarIA — Detector de PostGIS
echo ============================================
echo.

REM Detectar psql
where psql >nul 2>&1
if errorlevel 1 (
    echo [ERROR] psql no esta en PATH. Instala PostgreSQL primero.
    echo   Descarga: https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)

REM Detectar version
for /f "tokens=3" %%i in ('psql --version') do set PG_VERSION=%%i
echo [OK] PostgreSQL detectado: %PG_VERSION%
echo.

REM Probar conexion a postgres database
set PGPASSWORD=postgres
psql -U postgres -c "SELECT 1" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] No se pudo conectar como usuario 'postgres'.
    echo         Posible contrasena incorrecta. Ajusta el archivo .env
    echo.
    pause
    exit /b 1
)
echo [OK] Conexion a PostgreSQL exitosa.
echo.

REM Verificar PostGIS disponible
echo Verificando PostGIS...
psql -U postgres -tAc "SELECT 1 FROM pg_available_extensions WHERE name='postgis';" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================
    echo  [FALTA] PostGIS no esta disponible
    echo ============================================
    echo.
    echo  OPCION A: Si instalaste Postgres con el instalador EDB:
    echo    1. Re-ejecuta el instalador de PostgreSQL
    echo    2. Al final marca "Stack Builder"
    echo    3. Selecciona tu version (%PG_VERSION%) y abajo "PostGIS"
    echo    4. Acepta defaults
    echo.
    echo  OPCION B: Instalador standalone:
    echo    1. Ve a https://postgis.net/windows_downloads/
    echo    2. Descarga la version %PG_VERSION%
    echo    3. Instala con defaults
    echo.
    echo  Despues de instalar, ejecuta este script de nuevo.
    echo ============================================
    echo.
    pause
    exit /b 1
)

echo [OK] PostGIS esta disponible.
psql -U postgres -tAc "SELECT PostGIS_Version();" 2>nul
echo.
echo ============================================
echo  Listo! PostGIS esta correctamente instalado.
echo ============================================
echo.
endlocal
