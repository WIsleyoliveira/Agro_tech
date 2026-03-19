# 🚀 Como Usar o VitaGreen - Guia Rápido

## ✅ Sistema Rodando!

O servidor está **ONLINE** em: **http://localhost:8000**

---

## 🌐 Acessar o Sistema

### 1. **Página Principal** (Análise de Solo)
```
http://localhost:8000
```
- Interface completa de análise
- Chat com IA agrícola
- **Dark Mode** disponível! (botão 🌙/☀️ no canto superior direito)

### 2. **Página de Login** (Sistema de Autenticação)
```
http://localhost:8000/login.html
```
- Criar conta nova
- Fazer login
- Ou continuar sem login

---

## 🎨 Dark Mode (NOVO!)

### Como Usar:
1. Clique no botão **🌙** no canto superior direito
2. O tema muda automaticamente para escuro ☀️
3. Sua preferência fica salva!

### Recursos:
- ✅ Detecta preferência do sistema automaticamente
- ✅ Persiste sua escolha no navegador
- ✅ Transições suaves
- ✅ Funciona em todas as páginas

---

## 📝 Como Fazer Análise de Solo

### Passo 1: Preencher Dados
1. **Básicos (obrigatórios):**
   - pH (0-14)
   - Umidade (%)

2. **Nutrientes (opcionais):**
   - Nitrogênio (N)
   - Fósforo (P)
   - Potássio (K)
   - Cálcio (Ca)
   - Magnésio (Mg)
   - Matéria Orgânica (MO)

3. **Cultura:** Escolha o tipo de plantação

### Passo 2: Analisar
- **Botão "Analisar":** Análise completa com IA
- **Botão "Rápida":** Análise básica rápida
- **Botão "Preencher exemplo":** Testa com dados de exemplo

### Passo 3: Ver Resultado
- Recomendações em **linguagem simples**
- Tags com os valores analisados
- Nível de confiança (Alta/Média/Preliminar)

---

## 💬 Como Usar o Chat

### Passo 1: Fazer Análise Primeiro
- O chat precisa dos dados do solo analisado

### Passo 2: Iniciar Sessão
- Clique em **"Iniciar sessão"**
- Os dados do solo serão carregados automaticamente

### Passo 3: Conversar
- Digite perguntas sobre:
  - Correção de pH
  - Adubação
  - Calagem
  - Problemas específicos
  
**Exemplos de perguntas:**
- "Como corrigir o pH do solo?"
- "Quanto de calcário aplicar?"
- "O nitrogênio está baixo, o que fazer?"

### Passo 4: Encerrar
- Clique em **"Encerrar"** quando terminar

---

## 🔐 Sistema de Login (Opcional)

### Criar Conta:
1. Acesse http://localhost:8000/login.html
2. Clique em **"Criar Conta"**
3. Preencha:
   - Nome completo
   - Email
   - Senha (mínimo 6 caracteres)
   - Telefone (opcional)
   - Nome da fazenda (opcional)
4. Clique em **"Criar Conta"**

### Fazer Login:
1. Acesse http://localhost:8000/login.html
2. Digite email e senha
3. Clique em **"Entrar"**

### Benefícios de Fazer Login:
- ✅ Histórico de análises salvo
- ✅ Acesso de qualquer lugar
- ✅ Dados seguros com JWT
- ✅ Senhas protegidas com hash

### Usar Sem Login:
- Clique em **"Continuar sem login"**
- Funciona normalmente, mas sem histórico

---

## 🛠️ Parar o Servidor

No terminal onde rodou `python main.py`:
```bash
Ctrl + C
```

---

## 🔄 Reiniciar o Servidor

```bash
cd /Users/wisley/Downloads/VitaGreenProjeto
python main.py
```

Depois acesse: http://localhost:8000

---

## 📊 API para Sensores (Avançado)

### Enviar Leitura do Sensor:
```bash
curl -X POST http://localhost:8000/api/sensor/reading \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "plantacao_01",
    "sample_id": 1,
    "ph": 6.5,
    "humidity": 45.2,
    "nitrogen": 120,
    "phosphorus": 80,
    "potassium": 150
  }'
```

### Buscar Sessão:
```bash
curl http://localhost:8000/api/sensor/session/plantacao_01
```

### Analisar Sessão:
```bash
curl -X POST http://localhost:8000/api/sensor/analyze_session/plantacao_01
```

---

## 🎯 Dicas de Uso

### Interface:
1. **Use "Preencher exemplo"** para testar rapidamente
2. **Selecione o tipo de solo** para conversões corretas
3. **Veja os valores em kg/ha** abaixo dos inputs de NPK

### Dark Mode:
1. **Modo escuro** economiza bateria em celulares OLED
2. **Melhor para usar à noite** ou em locais escuros
3. **Sua preferência fica salva** automaticamente

### Chat:
1. **Seja específico** nas perguntas
2. **Use o contexto** dos dados analisados
3. **Pergunte sobre ações práticas** (quanto aplicar, quando fazer)

### Autenticação:
1. **Email** precisa ser válido
2. **Senha** mínimo 6 caracteres
3. **Opcional:** Nome da fazenda ajuda na organização

---

## 🐛 Problemas Comuns

### "Ollama não está rodando"
**Solução:**
```bash
# Terminal separado
ollama serve
```

### "Module not found"
**Solução:**
```bash
pip install -r requirements.txt
```

### Página não carrega
**Verificar se o servidor está rodando:**
- Deve aparecer: "Uvicorn running on http://0.0.0.0:8000"
- Se não, rode: `python main.py`

### Dark mode não funciona
**Limpar cache do navegador:**
- Chrome/Edge: `Ctrl+Shift+Delete`
- Safari: `Cmd+Option+E`
- Ou use modo anônimo para testar

---

## 📱 Acesso pelo Celular

### Na mesma rede WiFi:
1. Descubra o IP do computador:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. No celular, acesse:
```
http://SEU_IP:8000
```

Exemplo: `http://192.168.1.100:8000`

---

## ✨ Recursos Implementados

### ✅ Core:
- [x] Análise de solo com IA local (Ollama)
- [x] Chat agrícola em linguagem simples
- [x] Banco de dados SQLite
- [x] API REST completa

### ✅ Autenticação:
- [x] Sistema de login/registro
- [x] JWT tokens (seguro)
- [x] Senhas com hash BCrypt
- [x] Histórico de análises por usuário
- [x] Uso opcional (pode usar sem login)

### ✅ Interface:
- [x] Dark Mode com toggle
- [x] Detecção de preferência do sistema
- [x] Persistência de tema
- [x] Design moderno e responsivo
- [x] Conversões automáticas (mg/kg → kg/ha)

### ✅ Integração:
- [x] API para sensores IoT
- [x] Modo de amostragem múltipla
- [x] Cálculo de médias
- [x] Exportação de dados

---

## 💰 Custo

**ZERO! 🎉**
- Ollama é 100% gratuito
- Sem tokens de API
- Sem limite de uso
- Dados ficam no seu computador

---

## 📞 Suporte

**Checklist básico:**
1. ✅ Ollama rodando? (`ollama serve`)
2. ✅ Modelo instalado? (`ollama list`)
3. ✅ Python 3.8+? (`python --version`)
4. ✅ Dependências? (`pip install -r requirements.txt`)
5. ✅ Servidor rodando? (deve mostrar "Uvicorn running...")

---

**Desenvolvido para agricultores! 🌱**
*Sistema completo, gratuito e fácil de usar!*
