#!/usr/bin/env bash
# ==============================================================================
# Script de Despliegue Automatizado en Oracle Cloud Infrastructure (OCI)
# Proyecto: V.I.E.R.N.E.S. PhoneApp Academic
# Sistema: Ubuntu 22.04 / 24.04 LTS (Compatible con AMD64 y ARM64 Ampere A1)
# ==============================================================================

set -e

# Colores para salida de terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${GREEN}   DESPLIEGUE AUTOMÁTICO DE V.I.E.R.N.E.S. EN ORACLE CLOUD ALWAYS FREE       ${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# 1. Verificar directorio de ejecución
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 2. Actualizar paquetes base del sistema
echo -e "\n${YELLOW}[1/6] Actualizando paquetes del sistema...${NC}"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    iptables-persistent \
    netfilter-persistent

# 3. Instalar Docker y Docker Compose si no están instalados
echo -e "\n${YELLOW}[2/6] Verificando instalación de Docker y Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    echo "Instalando Docker Engine oficial..."
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Agregar usuario actual al grupo docker
    sudo usermod -aG docker "$USER"
    echo -e "${GREEN}Docker instalado exitosamente.${NC}"
else
    echo -e "${GREEN}Docker ya se encuentra instalado.${NC}"
fi

# 4. Configurar Firewall interno de Oracle Cloud (CRUCIAL)
# Por defecto, la imagen de Ubuntu en Oracle Cloud bloquea puertos que no sean el 22 en iptables.
echo -e "\n${YELLOW}[3/6] Abriendo puertos en el firewall interno de Oracle Cloud (iptables)...${NC}"
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# Persistir reglas para que no se pierdan al reiniciar la máquina
sudo netfilter-persistent save || true

# Si UFW está activo, también permitir puertos
if command -v ufw &> /dev/null && sudo ufw status | grep -q "Status: active"; then
    echo "Permitiendo puertos en UFW..."
    sudo ufw allow 80/tcp || true
    sudo ufw allow 443/tcp || true
    sudo ufw allow 8000/tcp || true
fi
echo -e "${GREEN}Puertos 80, 443 y 8000 desbloqueados en el sistema operativo.${NC}"

# 5. Preparar archivo de entorno (.env) y carpetas persistentes
echo -e "\n${YELLOW}[4/6] Configurando almacenamiento y entorno...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creando .env a partir de .env.example...${NC}"
        cp .env.example .env
        echo -e "${RED}IMPORTANTE: Recuerda editar '.env' con tus claves API (nano .env)${NC}"
    else
        touch .env
    fi
fi

mkdir -p ./data/downloads
mkdir -p ./data/generated_docs
mkdir -p ./data/Moodle_PSM_Estudio
mkdir -p ./caddy_data
mkdir -p ./caddy_config

# Si existe una base de datos local en backend/phoneapp.db y no en ./data/phoneapp.db, migrarla
if [ -f "backend/phoneapp.db" ] && [ ! -f "data/phoneapp.db" ]; then
    echo "Copiando base de datos inicial a almacenamiento persistente..."
    cp backend/phoneapp.db data/phoneapp.db
fi

# Ajustar permisos para que el contenedor pueda escribir
chmod -R 777 ./data

# 6. Levantar contenedores con Docker Compose
echo -e "\n${YELLOW}[5/6] Construyendo y levantando contenedores con Docker Compose...${NC}"
# Usar docker compose (plugin moderno) o docker-compose (legacy)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif sudo docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="sudo docker compose"
else
    DOCKER_COMPOSE_CMD="sudo docker-compose"
fi

$DOCKER_COMPOSE_CMD down || true
$DOCKER_COMPOSE_CMD up -d --build

# 7. Verificar estado y obtener IP pública
echo -e "\n${YELLOW}[6/6] Verificando estado del servicio...${NC}"
sleep 5
$DOCKER_COMPOSE_CMD ps

PUBLIC_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || echo "TU_IP_PUBLICA")

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   ¡V.I.E.R.N.E.S. DESPLEGADO EXITOSAMENTE EN ORACLE CLOUD!                   ${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "Puedes acceder desde tu navegador o teléfono en:"
echo -e "  - ${BLUE}Interfaz Web (Caddy):${NC}  http://${PUBLIC_IP}"
echo -e "  - ${BLUE}API / Docs Swagger:${NC}   http://${PUBLIC_IP}:8000/docs"
echo -e "  - ${BLUE}Health Check:${NC}         http://${PUBLIC_IP}:8000/api/health"
echo ""
echo -e "Nota sobre Oracle Cloud:"
echo -e "Asegúrate de haber creado las ${YELLOW}Reglas de Entrada (Ingress Rules)${NC} en la consola"
echo -e "de Oracle Cloud (VCN -> Security Lists) para los puertos ${GREEN}80, 443 y 8000${NC}."
echo ""
echo -e "Para ver los logs en tiempo real:"
echo -e "  ${YELLOW}$DOCKER_COMPOSE_CMD logs -f app${NC}"
echo -e "${GREEN}==============================================================================${NC}"
