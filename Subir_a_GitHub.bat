@echo off
title Asistente para Subir a GitHub - V.I.E.R.N.E.S.
cd /d "%~dp0"

echo ==============================================================================
echo        VINCULAR Y SUBIR PROYECTO A GITHUB (V.I.E.R.N.E.S. PHONEAPP)
echo ==============================================================================
echo.

:: 1. Verificar si Git esta en el sistema
where git >nul 2>nul
if %errorlevel% neq 0 (
    set "PATH=%PATH%;C:\Program Files\Git\cmd;C:\Program Files\Git\bin"
)

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] Git no fue detectado en PATH. Por favor reinicia tu terminal o verifica la instalacion.
    pause
    exit /b 1
)

:: 2. Configurar usuario si no existe
for /f "tokens=*" %%i in ('git config --get user.name') do set GIT_USER=%%i
if "%GIT_USER%"=="" (
    echo Configurando identidad de Git por primera vez:
    set /p NEW_NAME="1. Ingresa tu Nombre o Usuario de GitHub: "
    set /p NEW_EMAIL="2. Ingresa tu Correo de GitHub: "
    git config --global user.name "%NEW_NAME%"
    git config --global user.email "%NEW_EMAIL%"
    echo [OK] Identidad guardada.
    echo.
)

:: 3. Solicitar URL del repositorio
echo Asegurate de haber creado el repositorio vacio en https://github.com/new
set /p REPO_URL="Pega la URL HTTPS de tu repositorio (ej. https://github.com/tu_usuario/viernes-academic.git): "

if "%REPO_URL%"=="" (
    echo [X] No ingresaste ninguna URL. Operacion cancelada.
    pause
    exit /b 1
)

:: 4. Inicializar, agregar archivos y hacer commit
echo.
echo [1/4] Inicializando repositorio y rama 'main'...
git init >nul 2>nul
git branch -M main

echo [2/4] Agregando archivos del proyecto...
git add .

echo [3/4] Creando commit inicial...
git commit -m "Deploy inicial V.I.E.R.N.E.S. Academic"

echo [4/4] Conectando con GitHub y subiendo cambios...
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

echo.
echo ==============================================================================
echo  IMPORTANTE: Se abrira una ventana de 'Git Credential Manager'.
echo  Haz clic en 'Sign in with your browser' y autoriza en tu navegador.
echo ==============================================================================
echo.
git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ==============================================================================
    echo  [OK] PROYECTO SUBIDO EXITOSAMENTE A TU GITHUB!
    echo ==============================================================================
    echo Ya puedes ir a Render.com y seleccionar este repositorio para desplegarlo.
) else (
    echo [!] Hubo un error al subir a GitHub. Revisa los mensajes arriba.
)

echo.
pause
