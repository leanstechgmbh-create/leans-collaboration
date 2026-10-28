@echo off
rem LEANS Bildschirm-Freigabe: einmal doppelklicken.
rem Danach startet sie bei jeder Windows-Anmeldung automatisch im Hintergrund.
rem Sie macht NUR auf Anfrage einen Screenshot in den Google-Drive-Ordner (kein Klicken, kein Tippen).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0leans-bildschirm.ps1" -Autostart
echo.
pause
