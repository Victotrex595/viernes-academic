@echo off
title Asistente para Subir a GitHub - V.I.E.R.N.E.S.
cd /d "%~dp0"

echo ==============================================================================
echo        VINCULAR Y SUBIR PROYECTO A GITHUB (V.I.E.R.N.E.S. PHONEAPP)
echo ==============================================================================
echo.

set "PATH=%PATH%;C:\Program Files\Git\cmd;C:\Program Files\Git\bin"

echo Repositorio detectado: https://github.com/Victotrex595/viernes-academic.git
echo Usuario configurado:   Victotrex595
echo.
echo ==============================================================================
echo  PASO FINAL: Se abrira una ventana de 'Git Credential Manager'.
echo  Haz clic en 'Sign in with your browser' para autorizar con tu cuenta.
echo ==============================================================================
echo.

git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ==============================================================================
    echo  [OK] PROYECTO SUBIDO EXITOSAMENTE A TU GITHUB!
    echo ==============================================================================
    echo Ya puedes ir a Render.com y seleccionar el repositorio 'viernes-academic'
    echo para desplegarlo de inmediato.
) else (
    echo [!] Si la ventana no subio los cambios, verifica que tu repositorio en GitHub
    echo     este creado en: https://github.com/Victotrex595/viernes-academic
)

echo.
pause
