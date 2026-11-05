# 🎓 Guía de Despliegue en Hugging Face Spaces (24/7 Gratis)
## Sistema Académico V.I.E.R.N.E.S. PhoneApp

Hugging Face Spaces es la mejor alternativa gratuita para desplegar **V.I.E.R.N.E.S.**:
- **100% Gratis de por vida**.
- **Cero bloqueos regionales** y no requiere tarjeta de crédito.
- **16 GB de Memoria RAM y 2 vCPUs** (mucha más potencia que los tiers gratuitos tradicionales).
- **HTTPS / SSL Automático** con URL pública lista para tu teléfono (`https://tu-usuario-viernes-academic.hf.space`).

---

### 🔑 Paso Previo: Obtener tu Token de Hugging Face (1 minuto)

Para que el asistente pueda crear tu Space y subir el código automáticamente:

1. Ve a tu cuenta de Hugging Face en: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Haz clic en el botón **Create new token**.
3. Configura:
   - **Token name**: `viernes-token`
   - **Token type**: Selecciona **Write** (o si aparece lista granular, selecciona permisos de escritura en *Spaces*).
4. Haz clic en **Create token** y cópialo (empieza por `hf_...`).

---

### 🚀 Método 1: Despliegue Automático en 1 Clic (Recomendado)

Ya dejamos preparado un asistente automático que sube tu proyecto, crea el Space y configura tus claves API encriptadas sin que tengas que usar Git ni comandos raros:

1. En tu computadora, ve a la carpeta:
   `c:\Users\Admin\Documents\Phoneapp`
2. Haz doble clic en el archivo:
   **`Subir_a_HuggingFace.bat`**
3. El asistente te pedirá:
   - Pegar tu Token de Hugging Face (`hf_...`).
   - Confirmar el nombre del Space (por defecto: `viernes-academic`).
4. **¡Listo!** El script:
   - Creará el Space automáticamente con soporte Docker.
   - Sincronizará tus claves de `.env` (Gemini, DeepSeek, Drive Bridge, SAIA) como secretos encriptados en Hugging Face.
   - Subirá los archivos del servidor y la base de datos con los cursos ya sincronizados.
   - Te entregará tu enlace directo para el teléfono.

---

### 🌐 Método 2: Manual desde la Web de Hugging Face (Alternativa)

Si prefieres hacerlo manualmente a través de la interfaz web:

#### 1. Crear el Space
1. Ve a [https://huggingface.co/new-space](https://huggingface.co/new-space).
2. **Space name**: `viernes-academic`.
3. **License**: `mit` o la que prefieras.
4. **Space SDK**: Selecciona **Docker** > **Blank**.
5. **Space hardware**: `CPU basic · 2 vCPU · 16 GB · Free`.
6. **Visibility**: `Public` (o `Private` si prefieres que solo tú puedas verlo iniciando sesión).
7. Haz clic en **Create Space**.

#### 2. Configurar los Secretos (Claves API)
En tu Space recién creado:
1. Ve a la pestaña **Settings** (arriba a la derecha).
2. Baja hasta la sección **Variables and secrets**.
3. Haz clic en **New secret** y agrega cada una de tus variables de `.env`:
   - `GEMINI_API_KEY`: Tu clave de Google AI Studio.
   - `GEMINI_API_KEY_2`: Tu segunda clave de Google (opcional).
   - `DEEPSEEK_API_KEY`: Tu clave de DeepSeek.
   - `GOOGLE_DRIVE_BRIDGE_URL`: Tu URL del Apps Script.
   - `SAIA_USERNAME`: Tu cédula/usuario de SAIA.
   - `SAIA_PASSWORD`: Tu clave de SAIA.

#### 3. Subir los Archivos
En la pestaña **Files**:
1. Haz clic en **Add file** > **Upload files**.
2. Sube los archivos `Dockerfile`, `README.md`, y la carpeta `backend/` (con `app/`, `requirements.txt` y `phoneapp.db`).
3. Haz clic en **Commit changes to main**.

---

### 📱 Cómo Usar la Aplicación desde tu Teléfono

1. Una vez que el Space termine de compilar (verás el estado en verde: **Running**), obtendrás tu URL directa:
   ```
   https://<tu-usuario>-viernes-academic.hf.space
   ```
2. Abre esa URL en el navegador de tu teléfono (Chrome o Safari).
3. **Instalar como App Móvil (PWA)**:
   - En Android (Chrome): Toca los 3 puntos arriba a la derecha y selecciona **"Agregar a la pantalla de inicio"** o **"Instalar aplicación"**.
   - En iPhone (Safari): Toca el botón Compartir (cuadrado con flecha) y selecciona **"Agregar al inicio"**.
4. ¡Tendrás el icono de **V.I.E.R.N.E.S.** en tu pantalla de inicio funcionando las 24 horas del día sin depender de que tu computadora esté encendida!
