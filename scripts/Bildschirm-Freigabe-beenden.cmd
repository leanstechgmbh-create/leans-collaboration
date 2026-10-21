@echo off
rem LEANS Bildschirm-Freigabe beenden und Autostart entfernen.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0leans-bildschirm.ps1" -AutostartEntfernen
echo.
pause
