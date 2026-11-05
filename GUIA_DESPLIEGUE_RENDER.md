# 🚀 Guía de Despliegue en Render.com (24/7 Gratis)
## Sistema Académico V.I.E.R.N.E.S. PhoneApp

Como ya tienes experiencia con Render y UptimeRobot para tu bot de Telegram, este despliegue te resultará sumamente familiar y cómodo.

---

### Paso 1: Crear el Repositorio en GitHub

1. Entra a tu cuenta en [github.com/new](https://github.com/new).
2. Asigna un nombre: por ejemplo `viernes-academic` (o `phoneapp-academic`).
3. Elige la visibilidad: **Private** (recomendado) o **Public**.
4. Haz clic en **Create repository**.
5. Sube los archivos del proyecto:
   * Puedes usar **"uploading an existing file"** en la web de GitHub y arrastrar la carpeta `backend/`, el archivo `render.yaml`, `Dockerfile` y `README.md`.
   * O si tienes Git configurado en tu terminal:
     ```bash
     git init
     git add .
     git commit -m "Initial commit V.I.E.R.N.E.S."
     git branch -M main
     git remote add origin https://github.com/TU_USUARIO/viernes-academic.git
     git push -u origin main
     ```

---

### Paso 2: Crear el Web Service en Render.com

1. Entra a tu panel de [dashboard.render.com](https://dashboard.render.com/).
2. Haz clic en **New +** > **Web Service**.
3. Selecciona **Build and deploy from a Git repository** y haz clic en *Next*.
4. Conecta tu repositorio recién creado (`viernes-academic`).
5. Configura los parámetros:
   * **Name**: `viernes-academic`
   * **Region**: `Oregon (US West)` u `Ohio (US East)`
   * **Branch**: `main`
   * **Root Directory**: *(Dejar en blanco)*
   * **Runtime**: **Python 3**
   * **Build Command**:
     ```bash
     pip install -r backend/requirements.txt
     ```
   * **Start Command**:
     ```bash
     python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend
     ```
   * **Instance Type**: Selecciona **Free** ($0 / month).

---

### Paso 3: Configurar las Variables de Entorno en Render

En la misma pantalla (o en la pestaña **Environment** de tu servicio en Render), agrega tus claves:

| Variable | Valor sugerido |
| :--- | :--- |
| `PYTHON_VERSION` | `3.12.4` |
| `PHONEAPP_DATA_DIR` | `/tmp/data` |
| `GEMINI_API_KEY` | *(Tu clave principal de Gemini)* |
| `GEMINI_API_KEY_2` | *(Tu segunda clave de Gemini, opcional)* |
| `GEMINI_API_KEY_3` | *(Tu tercera clave de Gemini, opcional)* |
| `DEEPSEEK_API_KEY` | *(Tu clave de DeepSeek)* |
| `GOOGLE_DRIVE_BRIDGE_URL` | *(La URL de tu Apps Script de Google Drive)* |
| `SAIA_USERNAME` | *(Tu usuario o cédula de SAIA)* |
| `SAIA_PASSWORD` | *(Tu contraseña de SAIA)* |

Haz clic en **Create Web Service**. Render comenzará a compilar e instalar las dependencias. En unos 2 a 3 minutos verás el estado en verde: **Live**.

---

### Paso 4: Mantenerlo Despierto 24/7 con UptimeRobot

Dado que los Web Services gratuitos de Render entran en suspensión tras 15 minutos sin visitas:

1. Copia tu URL de Render: `https://viernes-academic.onrender.com`
2. Ve a tu cuenta de [uptimerobot.com](https://uptimerobot.com/).
3. Haz clic en **Add New Monitor**:
   * **Monitor Type**: `HTTP(s)`
   * **Friendly Name**: `Viernes Academic Backend`
   * **URL (or IP)**: `https://viernes-academic.onrender.com/api/health`
   * **Monitoring Interval**: Cada `5 minutes` (o 10 minutes).
4. Haz clic en **Create Monitor**.

¡Listo! UptimeRobot enviará una señal a `/api/health` cada 5 minutos, impidiendo que Render se duerma y manteniéndolo activo las 24 horas del día.

---

### 📱 Acceso desde tu Teléfono

1. Abre en tu celular: `https://viernes-academic.onrender.com`
2. Toca **"Agregar a la pantalla de inicio"** para instalar la App PWA.
3. Tendrás tu asistente con Gemini, DeepSeek, Moodle SAIA y Word completamente disponible en la nube sin necesidad de tener tu computadora encendida.
