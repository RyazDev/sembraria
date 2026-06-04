@echo off
REM ====================================================================
REM  SEMBRARIA — Setup de Base de Datos
REM  Crea la DB 'sembraria', corre los scripts init-db/*.sql en orden.
REM ====================================================================
setlocal enabledelayedexpansion

echo.
echo ============================================
echo  SembrarIA — Setup de Base de Datos
echo ============================================
echo.

REM Verificar PostGIS primero
call "%~dp0install-postgis.bat"
if errorlevel 1 (
    echo [ABORTADO] PostGIS no esta disponible. Instala primero.
    pause
    exit /b 1
)

REM Verificar .env en la RAIZ del proyecto (2 niveles arriba de scripts/setup/)
if not exist "%~dp0..\..\.env" (
    if not exist "%~dp0..\..\apps\api\.env.example" (
        echo [ERROR] No se encuentra .env ni apps\api\.env.example
        exit /b 1
    )
    echo [AVISO] .env no existe en la raiz. Copiando desde apps\api\.env.example...
    copy "%~dp0..\..\apps\api\.env.example" "%~dp0..\..\.env" >nul
    echo [OK] .env creado en la raiz. Editalo con tus credenciales.
    echo.
    echo       Presiona cualquier tecla para abrir el editor, o Ctrl+C para abortar...
    pause >nul
    notepad "%~dp0..\..\.env"
)

REM Pedir credenciales de postgres (no asumimos password por seguridad)
set /p PGUSER="Usuario postgres [postgres]: "
if "%PGUSER%"=="" set PGUSER=postgres
set /p PGPASSWORD="Password de %PGUSER%: "
set /p PGDATABASE="Nombre de la BD [sembraria]: "
if "%PGDATABASE%"=="" set PGDATABASE=sembraria

echo.
echo [1/3] Eliminando DB '%PGDATABASE%' si existe (reset)...
psql -U %PGUSER% -c "DROP DATABASE IF EXISTS %PGDATABASE%;" 2>nul
if errorlevel 1 (
    echo [AVISO] No se pudo eliminar. Continuando...
)

REM Crear DB
echo [2/3] Creando DB '%PGDATABASE%'...
psql -U %PGUSER% -c "CREATE DATABASE %PGDATABASE%;"
if errorlevel 1 (
    echo [ERROR] No se pudo crear la DB
    pause
    exit /b 1
)

REM Correr scripts config\db\*.sql en orden (2 niveles arriba: raiz del proyecto)
echo [3/3] Corriendo scripts config\db\*.sql...
for %%f in ("%~dp0..\..\config\db\*.sql") do (
    echo.
    echo   Ejecutando %%~nxf...
    psql -U %PGUSER% -d %PGDATABASE% -v ON_ERROR_STOP=1 -f "%%f" -q
    if errorlevel 1 (
        echo [ERROR] Fallo en %%~nxf
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo  [OK] Base de datos '%PGDATABASE%' lista!
echo ============================================
echo.
echo   Tablas creadas:
psql -U %PGUSER% -d %PGDATABASE% -c "\dt" 2>nul
echo.
echo   Funcion geoespacial disponible:
psql -U %PGUSER% -d %PGDATABASE% -c "\df is_within_caqueta" 2>nul
echo.
echo   Siguiente paso: scripts\setup\setup-backend.bat
echo.
endlocal
pause
