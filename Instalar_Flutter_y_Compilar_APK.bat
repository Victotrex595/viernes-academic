@echo off
title Instalador de Flutter SDK y Compilador APK - PhoneApp
cd /d "C:\Users\Admin\Documents\Phoneapp"

echo ============================================================================
echo   PREPARACION DE FLUTTER SDK Y COMPILACION DE APK ANDROID
echo ============================================================================

set "ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk"
set "FLUTTER_DIR=C:\src\flutter"

where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if not exist "%FLUTTER_DIR%\bin\flutter.bat" (
        echo [1/3] Descargando Git y Flutter SDK oficial para Windows...
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        git clone https://github.com/flutter/flutter.git -b stable "%FLUTTER_DIR%"
    )
    set "PATH=%FLUTTER_DIR%\bin;%PATH%"
)

cd /d "C:\Users\Admin\Documents\Phoneapp\mobile_app"
echo [2/3] Inicializando estructura nativa Android en mobile_app...
call flutter create . --platforms=android
call flutter pub get

echo [3/3] Compilando APK de lanzamiento...
call flutter build apk --release

echo.
echo ============================================================================
echo   APK generado en: mobile_app\build\app\outputs\flutter-apk\app-release.apk
echo ============================================================================
pause
