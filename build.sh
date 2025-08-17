#!/bin/bash

# Script para build da imagem Docker da API de Transcrição de Áudio

echo "�� Iniciando build da imagem Docker..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Arquivo .env não encontrado. Criando arquivo padrão..."
    cat > .env << EOF
# Configurações da API
ENVIRONMENT=production
LOG_LEVEL=INFO
API_PORT=8000
EOF
fi

# Carregar variáveis de ambiente do arquivo .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build da imagem Docker
echo "�� Construindo imagem Docker..."
docker build \
  --build-arg GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --build-arg SECRET_KEY="$SECRET_KEY" \
  --build-arg API_KEY="$API_KEY" \
  -t medical-ai-api .

docker run -d \
  -p 8005:8005 \
  -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e API_KEY="$API_KEY" \
  medical-ai-api

if [ $? -eq 0 ]; then
    echo "✅ Imagem construída com sucesso!"
    echo "📋 Para executar: docker run -p 8000:8000 medical-ai-api"
else
    echo "❌ Falha ao construir imagem"
    exit 1
fi
