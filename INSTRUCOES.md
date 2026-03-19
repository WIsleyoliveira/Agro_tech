# 🌱 INSTRUÇÕES - VitaGreen v4.0

## ✅ O QUE FOI FEITO

Transformei seu projeto para usar **Ollama local** ao invés do Gemini (Google API paga).

### Arquivos Criados:
1. **ollama_service.py** - Conexão com IA local (Ollama)
2. **database.py** - Banco de dados SQLite para salvar leituras
3. **app.js** - JavaScript para o frontend
4. **README.md** - Documentação completa

### Arquivos Modificados:
- **main.py** - Atualizado para usar Ollama e banco de dados
- **requirements.txt** - Removido google-genai, adicionado requests

### Backups criados:
- main_backup.py
- index_backup.html

## 🚀 COMO USAR

### 1. Instalar Ollama

```bash
# macOS
brew install ollama

# Baixar modelo
ollama pull llama2:3b

# IMPORTANTE: Deixar rodando em um terminal separado
ollama serve
```

### 2. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 3. Iniciar o servidor

```bash
python main.py
```

### 4. Abrir no navegador

```
http://localhost:8000
```

## 💡 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Análise de Solo Simples
- Entrada manual de dados (pH, umidade, NPK)
- Linguagem simples e prática
- Recomendações diretas para agricultores

### ✅ Chat Amigável
- Conversa natural sobre agricultura
- Sem termos técnicos
- Foca em soluções práticas

### ✅ Integração com Sensor
- Endpoint `/api/sensor/reading` para receber dados
- Salva automaticamente no banco SQLite
- Calcula médias de múltiplas leituras

### ✅ Banco de Dados
- SQLite local (agrisensi.db)
- Histórico completo de medições
- Sessões de amostragem

## 📡 API PARA INTEGRAÇÃO COM SENSOR

### Enviar leitura do sensor:

```javascript
// POST /api/sensor/reading
{
  "session_id": "plantacao_norte_01",
  "sample_id": 1,
  "ph": 6.5,
  "humidity": 45.2,
  "nitrogen": 120,
  "phosphorus": 80,
  "potassium": 150,
  "timestamp": "2026-03-06T10:30:00"
}
```

### Buscar dados de uma sessão:

```javascript
// GET /api/sensor/session/plantacao_norte_01
// Retorna todas as leituras + média calculada
```

### Analisar sessão:

```javascript
// POST /api/sensor/analyze_session/plantacao_norte_01
// Analisa a média de todas as leituras com IA
```

## 🎨 PRÓXIMOS PASSOS SUGERIDOS

1. **Melhorar o frontend HTML**
   - Criar interface mais visual e didática
   - Adicionar ícones e imagens
   - Fazer responsivo para celular

2. **Integração física do sensor**
   - Conectar Arduino/Raspberry Pi
   - Enviar dados via WiFi/Bluetooth
   - Automatizar coleta de dados

3. **Recursos adicionais**
   - Gráficos de histórico
   - Comparação entre áreas
   - Alertas automáticos
   - Exportar relatórios PDF

## 🐛 SOLUÇÃO DE PROBLEMAS

**Erro: "Ollama não está rodando"**
```bash
# Terminal 1
ollama serve

# Terminal 2
python main.py
```

**Erro: "Model llama2:3b not found"**
```bash
ollama pull llama2:3b
```

**Erro de permissão no banco**
```bash
chmod u+w agrisensi.db
```

## 💰 CUSTOS

**ZERO!** 🎉

- Ollama é 100% gratuito e local
- Não consome tokens de API
- Seus dados ficam no seu computador
- Sem limite de uso

## 📞 SUPORTE

Qualquer dúvida, verifique:
1. Ollama está rodando? (`ollama serve`)
2. Modelo foi baixado? (`ollama list`)
3. Python 3.8+? (`python --version`)

---

**Desenvolvido para agricultores, com linguagem simples e foco em soluções práticas! 🌱**
