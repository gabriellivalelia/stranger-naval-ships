#!/bin/bash

# Stranger Naval Ships - Script de inicialização

echo "🚢 Stranger Naval Ships"
echo "======================="
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker não encontrado. O jogo rodará em modo offline."
    echo ""
    echo "Para instalar Docker: https://docs.docker.com/get-docker/"
    echo ""
else
    # Verifica se o Docker Compose está disponível
    if command -v docker compose &> /dev/null; then
        echo "🐳 Iniciando MongoDB com Docker Compose..."
        docker compose up -d
        
        if [ $? -eq 0 ]; then
            echo "✅ MongoDB iniciado com sucesso!"
            echo ""
            # Aguarda um momento para o MongoDB estar pronto
            sleep 2
        else
            echo "⚠️  Erro ao iniciar MongoDB. Usando modo offline."
            echo ""
        fi
    else
        echo "⚠️  Docker Compose não encontrado. Usando modo offline."
        echo ""
    fi
fi

# Verifica se uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ uv não encontrado. Instale com: pip install uv"
    exit 1
fi

# Inicia o jogo
echo "🎮 Iniciando o jogo..."
echo ""
uv run python src/main.py
