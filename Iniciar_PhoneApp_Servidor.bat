@echo off
title Servidor PhoneApp Academica
cd /d "C:\Users\Admin\Documents\Phoneapp\backend"

echo ============================================================================
echo   PHONEAPP ACADEMICA: SAIA PSM + CONSORCIO IA (Gemini + DeepSeek-R1)
echo ============================================================================
echo.
echo   [+] Abre desde el navegador de tu telefono (mismo Wi-Fi):
echo       http://192.168.0.104:8000
echo.
echo   [+] Acceso local en esta PC:
echo       http://127.0.0.1:8000
echo ============================================================================
echo.

"C:\Users\Admin\Documents\Phoneapp\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
