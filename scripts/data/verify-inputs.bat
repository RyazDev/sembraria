@echo off
REM ====================================================================
REM  SEMBRARIA — Verifica que los 6 GeoTIFFs existan
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Verificando rasters
echo ============================================
echo.

set MISSING=0
set FOUND=0

for %%f in (aptitud_CACAO.tif aptitud_PLATANO.tif aptitud_YUCA.tif clasificacion_5clases.tif sintesis_mejor_cultivo.tif stack_54features.tif) do (
    if exist "%~dp0..\data\inputs\%%f" (
        for %%s in ("%~dp0..\data\inputs\%%f") do echo   [OK] %%f - %%~zs bytes
        set /a FOUND+=1
    ) else (
        echo   [FALTA] %%f
        set /a MISSING+=1
    )
)

echo.
echo Encontrados: %FOUND%/6
echo Faltantes: %MISSING%/6
echo.

if %MISSING% GTR 0 (
    echo Para generar los faltantes: scripts\generate-data.bat
    pause
    exit /b 1
)

echo [OK] Todos los rasters presentes.
echo.
endlocal
pause
