@echo off
REM ====================================================================
REM  SEMBRARIA — Reset DB (drop + recreate + re-seed)
REM ====================================================================
setlocal

echo.
echo ============================================
echo  SembrarIA — Reset DB
echo ============================================
echo.

call "%~dp0setup-db.bat"
endlocal
