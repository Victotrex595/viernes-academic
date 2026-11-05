@echo off
title V.I.E.R.N.E.S. - Servidor con Acceso Remoto para Celular
cd /d "%~dp0"

echo ==============================================================================
echo       INICIANDO V.I.E.R.N.E.S. PHONEAPP CON TUNEL SEGURO HTTPS
echo ==============================================================================
echo.

if exist "backend\.venv\Scripts\python.exe" (
    "backend\.venv\Scripts\python.exe" iniciar_remoto.py
) else (
    python iniciar_remoto.py
)

echo.
pause
