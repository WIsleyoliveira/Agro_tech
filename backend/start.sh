#!/bin/bash

echo "🌱 Iniciando AgroTech Platform..."

# Verificar se Java está instalado
if ! command -v java &> /dev/null; then
    echo "❌ Java não encontrado. Instale Java 17 ou superior."
    exit 1
fi

# Verificar se Maven está instalado
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven não encontrado. Instalando..."
    
    # Tentar instalar via Homebrew (macOS)
    if command -v brew &> /dev/null; then
        brew install maven
    else
        echo "Por favor, instale Maven manualmente: https://maven.apache.org"
        exit 1
    fi
fi

# Verificar variável de ambiente GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY não configurada!"
    echo ""
    echo "Para usar IA, obtenha uma chave em: https://makersuite.google.com/app/apikey"
    echo "E execute: export GEMINI_API_KEY='sua-chave-aqui'"
    echo ""
    read -p "Continuar sem IA? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ir para diretório do backend
cd "$(dirname "$0")"

# Compilar projeto
echo "📦 Compilando projeto..."
mvn clean install -DskipTests

# Executar aplicação
echo "🚀 Iniciando servidor..."
echo ""
echo "Backend: http://localhost:8080/api"
echo "H2 Console: http://localhost:8080/api/h2-console"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

mvn spring-boot:run
