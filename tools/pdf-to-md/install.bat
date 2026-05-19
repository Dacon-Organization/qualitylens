@echo off
setlocal
cd /d "%~dp0"

echo pdf-to-md student installer
echo This wrapper runs PowerShell with a conservative execution policy bypass for this install only.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 exit /b %errorlevel%

echo.
echo If Windows still cannot find uv, python, or java after installation,
echo restart Windows and run this installer again.
echo.
pause
