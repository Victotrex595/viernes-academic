# 🚀 Guía Definitiva de Despliegue en Oracle Cloud (OCI Always Free)
## Sistema Académico V.I.E.R.N.E.S. PhoneApp

Esta guía detalla paso a paso cómo desplegar el servidor backend y la interfaz web móvil de **V.I.E.R.N.E.S.** en una máquina virtual gratuita de por vida (**Always Free**) de **Oracle Cloud Infrastructure (OCI)**.

---

### 🏛️ Arquitectura del Despliegue

```
                                  INTERNET
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                     │
           Puerto 80 / 443                       Puerto 8000 (Opcional)
         (Web PWA / Teléfonos)                    (Swagger Docs / API)
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │    Caddy Proxy      │               │                     │
        │ (SSL Auto / Gzip)   │──────────────▶│  FastAPI Backend    │
        └─────────────────────┘   Red Docker  │  (Python 3.12 Slim) │
                                              │                     │
                                              └──────────┬──────────┘
                                                         │
                                               Volumen Persistente
                                                    (./data)
                                                         │
                                              ┌──────────┴──────────┐
                                              │ - phoneapp.db       │
                                              │ - generated_docs/   │
                                              │ - Moodle_PSM_...    │
                                              └─────────────────────┘
```

---

### Paso 1: Crear la Máquina Virtual en Oracle Cloud

1. Inicia sesión en tu consola de [Oracle Cloud](https://cloud.oracle.com/).
2. En el menú de navegación (arriba a la izquierda), ve a **Compute** > **Instances**.
3. Haz clic en **Create instance**.
4. Configura los parámetros:
   - **Name**: `viernes-academic-server`
   - **Image and shape**:
     - Haz clic en *Edit*.
     - **Image**: Selecciona **Ubuntu** (versión `22.04 LTS` o `24.04 LTS`).
     - **Shape**: 
       - *Opción Recomendada (Potente)*: Haz clic en *Change Shape* > **Ampere** (ARM) > `VM.Standard.A1.Flex`. Puedes asignar hasta **2 o 4 OCPUs** y **12 a 24 GB de RAM** totalmente **gratis de por vida**.
       - *Opción Alternativa (Micro)*: **AMD** > `VM.Standard.E2.1.Micro` (1 OCPU, 1 GB RAM).
   - **Networking**:
     - Deja la VCN y Subred pública por defecto.
     - Asegúrate de que esté marcado **Assign a public IPv4 address**.
   - **Add SSH keys**:
     - Selecciona **Generate a key pair for me** y haz clic en **Save private key** (descarga el archivo `.key` a tu computadora, por ejemplo en `C:\Users\Admin\Documents\oracle_key.key`).
5. Haz clic en **Create**. En unos minutos el estado cambiará a **Running** y verás la **Public IP** asignada.

---

### Paso 2: Abrir los Puertos en el Firewall de Oracle Cloud (Ingress Rules)

> [!IMPORTANT]
> Oracle Cloud bloquea todos los puertos por defecto en la red externa. Debes permitir los puertos 80, 443 y 8000 para que tu teléfono y navegador puedan conectarse.

1. En la página de detalles de tu instancia, en la sección **Instance information**, haz clic en el enlace de tu **Subnet** (o ve a **Networking** > **Virtual cloud networks** > tu VCN).
2. Haz clic en **Security Lists** y selecciona **Default Security List for...**.
3. Haz clic en **Add Ingress Rules**.
4. Agrega una regla para el tráfico web:
   - **Source Type**: `CIDR`
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `80,443,8000`
   - **Description**: `Viernes Web, SSL y API`
5. Haz clic en **Add Ingress Rules**.

---

### Paso 3: Conectar por SSH desde Windows

Abre PowerShell en tu computadora y conéctate usando la llave privada descargada:

```powershell
ssh -i "C:\ruta\de\tu\oracle_key.key" ubuntu@<TU_IP_PUBLICA>
```
*(Reemplaza `<TU_IP_PUBLICA>` con la dirección IP que te dio Oracle).*

---

### Paso 4: Subir el Proyecto a la Instancia

Desde tu máquina local (PowerShell en Windows), sube la carpeta `Phoneapp` a tu servidor:

```powershell
scp -i "C:\ruta\de\tu\oracle_key.key" -r "c:\Users\Admin\Documents\Phoneapp" ubuntu@<TU_IP_PUBLICA>:~/Phoneapp
```

> [!TIP]
> Si prefieres usar Git, en la instancia puedes clonar tu repositorio privado con:
> `git clone https://github.com/tu-usuario/tu-repo.git Phoneapp`

---

### Paso 5: Configurar el Archivo `.env` en el Servidor

Conéctate por SSH y ve a la carpeta del proyecto:

```bash
cd ~/Phoneapp
cp .env.example .env
nano .env
```

Configura tus credenciales:
```env
# Claves Gemini (puedes poner 1, 2 o más para rotación automática gratuita)
GEMINI_API_KEY=AIzaSy...
GEMINI_API_KEY_2=AIzaSy...

# Clave DeepSeek
DEEPSEEK_API_KEY=sk-...

# Google Drive Bridge (URL del Apps Script)
GOOGLE_DRIVE_BRIDGE_URL=https://script.google.com/macros/s/.../exec

# Moodle SAIA
SAIA_USERNAME=tu_cedula
SAIA_PASSWORD=tu_clave

# Si tienes dominio o subdominio gratuito (ej. DuckDNS), colócalo aquí para HTTPS automático:
DOMAIN=
```
*(Presiona `Ctrl + O` y luego `Enter` para guardar, y `Ctrl + X` para salir de nano).*

---

### Paso 6: Ejecutar el Despliegue Automatizado (1 Solo Comando)

Dale permisos de ejecución al script de despliegue y córrelo:

```bash
chmod +x deploy_oracle_cloud.sh
./deploy_oracle_cloud.sh
```

El script se encargará automáticamente de:
1. Instalar **Docker Engine** y **Docker Compose**.
2. Desbloquear las reglas internas de `iptables` de Ubuntu en Oracle Cloud (que suelen causar que no haya conexión aunque el puerto esté abierto en la consola).
3. Crear los volúmenes de almacenamiento persistente (`./data/`).
4. Compilar la imagen Docker multiplataforma y levantar los servicios con reinicio automático (`restart: unless-stopped`).

Al finalizar, verás en pantalla las URLs de acceso directo:
- **Interfaz Web Móvil (PWA)**: `http://<TU_IP_PUBLICA>`
- **Documentación Swagger / API**: `http://<TU_IP_PUBLICA>:8000/docs`

---

### Paso 7: Configuración de Dominio y SSL Gratis (Opcional pero Recomendado)

Si deseas tener un candado verde (`https://`) gratis para acceder desde cualquier parte:

1. Crea un subdominio gratuito en [DuckDNS](https://www.duckdns.org/) (por ejemplo: `miviernes.duckdns.org`) apuntando a tu `<TU_IP_PUBLICA>`.
2. En tu servidor, edita el archivo `.env`:
   ```bash
   nano .env
   ```
   Cambia la línea:
   ```env
   DOMAIN=miviernes.duckdns.org
   ```
3. Reinicia los contenedores:
   ```bash
   docker compose up -d --force-recreate caddy
   ```
   *¡Caddy solicitará y renovará automáticamente tu certificado SSL de Let's Encrypt sin configuración adicional!*

---

### 🛠️ Comandos Útiles de Mantenimiento

- **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f app
  ```
- **Ver estado de los contenedores:**
  ```bash
  docker compose ps
  ```
- **Reiniciar el servidor:**
  ```bash
  docker compose restart
  ```
- **Detener el servidor:**
  ```bash
  docker compose down
  ```
- **Actualizar cambios después de modificar código:**
  ```bash
  docker compose up -d --build
  ```
- **Copia de seguridad rápida de la base de datos:**
  ```bash
  cp data/phoneapp.db data/phoneapp_backup_$(date +%F).db
  ```
