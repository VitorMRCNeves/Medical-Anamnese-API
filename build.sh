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
docker build -t medical-ai-api .

if [ $? -eq 0 ]; then
    echo "✅ Imagem construída com sucesso!"
    echo "📋 Para executar: docker run -p 8000:8000 medical-ai-api"
else
    echo "❌ Falha ao construir imagem"
    exit 1
fi
