@echo off
title Desplegar V.I.E.R.N.E.S. a Hugging Face Spaces
cd /d "%~dp0"

echo ==============================================================================
echo       INICIANDO ASISTENTE DE DESPLIEGUE A HUGGING FACE SPACES
echo ==============================================================================
echo.

if exist "backend\.venv\Scripts\python.exe" (
    "backend\.venv\Scripts\python.exe" subir_a_huggingface.py
) else (
    python subir_a_huggingface.py
)

echo.
pause
