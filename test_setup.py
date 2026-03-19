#!/usr/bin/env python3
# test_setup.py - Testa se tudo está configurado

print("🌱 Testando configuração do VitaGreen v4.0...")
print()

# 1. Testar imports
print("1️⃣ Testando imports Python...")
try:
    import requests
    print("   ✅ requests instalado")
except ImportError:
    print("   ❌ requests não encontrado. Rode: pip install requests")

try:
    import sqlite3
    print("   ✅ sqlite3 disponível")
except ImportError:
    print("   ❌ sqlite3 não encontrado")

try:
    import fastapi
    print("   ✅ fastapi instalado")
except ImportError:
    print("   ❌ fastapi não encontrado. Rode: pip install fastapi")

try:
    import uvicorn
    print("   ✅ uvicorn instalado")
except ImportError:
    print("   ❌ uvicorn não encontrado. Rode: pip install uvicorn")

print()

# 2. Testar Ollama
print("2️⃣ Testando conexão com Ollama...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama está rodando!")
        models = response.json().get('models', [])
        if models:
            print(f"   📦 Modelos disponíveis: {len(models)}")
            for model in models:
                print(f"      - {model.get('name', 'unknown')}")
        else:
            print("   ⚠️  Nenhum modelo instalado. Rode: ollama pull llama2:3b")
    else:
        print(f"   ⚠️  Ollama respondeu com código {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama não está rodando!")
    print(f"      Inicie com: ollama serve")
    print(f"      Erro: {e}")

print()

# 3. Testar banco de dados
print("3️⃣ Testando banco de dados...")
try:
    from database import db
    print("   ✅ Banco de dados inicializado")
    print(f"   📂 Localização: agrisensi.db")
except Exception as e:
    print(f"   ❌ Erro ao inicializar banco: {e}")

print()

# 4. Resumo
print("=" * 50)
print("📋 RESUMO")
print("=" * 50)
print()
print("✅ Para iniciar o servidor:")
print("   python main.py")
print()
print("✅ Então abra no navegador:")
print("   http://localhost:8000")
print()
print("⚠️  IMPORTANTE: Se Ollama não estiver rodando:")
print("   Em outro terminal, execute: ollama serve")
print()
