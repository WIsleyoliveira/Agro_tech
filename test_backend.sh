#!/bin/bash

# Fazer login
echo "=== Fazendo login ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","senha":"senha123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo "Erro: Token não obtido"
    exit 1
fi

# Criar conversa
echo -e "\n=== Criando conversa ==="
CONVERSA_RESPONSE=$(curl -s -X POST http://localhost:8080/conversas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"tipoIA":"PORTUGUES","titulo":"Test Chat"}')

echo "$CONVERSA_RESPONSE"

CONVERSA_ID=$(echo $CONVERSA_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

echo "Conversa ID: $CONVERSA_ID"

if [ -z "$CONVERSA_ID" ]; then
    echo "Erro: Conversa não criada"
    exit 1
fi

# Enviar mensagem
echo -e "\n=== Enviando mensagem ==="
MENSAGEM_RESPONSE=$(curl -s -X POST http://localhost:8080/conversas/$CONVERSA_ID/mensagens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"conteudo":"Olá"}')

echo "$MENSAGEM_RESPONSE"
