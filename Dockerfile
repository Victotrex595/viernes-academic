# ==============================================================================
# Dockerfile para Hugging Face Spaces & Cloud Hosting
# Proyecto: V.I.E.R.N.E.S. PhoneApp Academic
# Compatible con Hugging Face Spaces (Port 7860, UID 1000) y Docker estándar
# ==============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    PYTHONPATH=/app \
    PHONEAPP_DATA_DIR=/app/data \
    PHONEAPP_PROJECT_ROOT=/app

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario estándar no-root (UID 1000) requerido por Hugging Face Spaces
RUN useradd -m -u 1000 user
ENV HOME=/home/user

# Copiar requerimientos e instalar dependencias de Python
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código del backend
COPY backend/app /app/app

# Crear directorios de datos y asignar permisos al usuario 1000
RUN mkdir -p /app/data/downloads \
             /app/data/generated_docs \
             /app/data/Moodle_PSM_Estudio && \
    chown -R user:user /app && \
    chmod -R 777 /app/data

# Si existe una base de datos local inicial, copiarla para mantener los cursos ya sincronizados
COPY --chown=user:user backend/phoneapp.db* /app/data/

USER user

# Hugging Face Spaces se comunica por el puerto 7860
EXPOSE 7860

# Healthcheck interno
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:7860/api/health || exit 1

# Arrancar Uvicorn en el puerto indicado por la plataforma (Render usa $PORT, por defecto 8000)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
