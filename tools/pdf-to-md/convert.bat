@echo off
setlocal
cd /d "%~dp0"

echo pdf-to-md converter
echo This wrapper runs PowerShell with a conservative execution policy bypass.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0convert.ps1"
if errorlevel 1 exit /b %errorlevel%

echo.
pause
