#!/bin/bash
# ==================== BUILD SCRIPT ====================
# Script para construir y ejecutar el contenedor Docker

set -e  # Salir si hay error

echo "🐳 ==================== EMOTION DETECTOR - DOCKER BUILD ===================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que existe .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo .env${NC}"
    echo "Copia .env.example a .env y configura tus variables"
    exit 1
fi

echo -e "${YELLOW}📦 Paso 1: Deteniendo contenedores existentes...${NC}"
docker-compose down 2>/dev/null || true

echo ""
echo -e "${YELLOW}🔨 Paso 2: Construyendo imagen Docker...${NC}"
docker-compose build --no-cache

echo ""
echo -e "${YELLOW}🚀 Paso 3: Iniciando contenedor...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}✅ ¡Contenedor iniciado exitosamente!${NC}"
echo ""
echo "📊 Dashboard disponible en: http://localhost:8000"
echo "📡 API docs en: http://localhost:8000/docs"
echo ""
echo "Ver logs en tiempo real:"
echo "  docker-compose logs -f"
echo ""
echo "Detener contenedor:"
echo "  docker-compose down"
echo ""
echo "==================== LISTO ===================="