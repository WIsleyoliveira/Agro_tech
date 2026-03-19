# 🚀 GUIA COMPLETO - AgroTech Platform

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Como Executar](#como-executar)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Funcionalidades](#funcionalidades)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### O Projeto

A **AgroTech Platform** é uma plataforma completa que resolve DOIS grandes desafios sociais:

#### 1. 📚 Educação Acessível
- **8 IAs Educacionais Especializadas**: Uma IA professor para cada matéria
- **Foco**: Estudantes de municípios com acesso precário à educação
- **Objetivo**: Democratizar educação de qualidade via IA
- **Matérias**: Português, Matemática, Química, Física, Biologia, Geografia, História, Ciências

#### 2. 🌾 Apoio ao Agronegócio Local
- **Agro.IA**: Consultoria agrícola inteligente para pequenos produtores
- **Mercado Local**: Plataforma de venda direta produtor-consumidor
- **Objetivo**: Fortalecer agricultura familiar e comércio local

### Por Que Isso Importa?

1. **Impacto Educacional**: Alunos sem acesso a professores qualificados podem ter IA personalizada 24/7
2. **Impacto Econômico**: Agricultores podem vender direto ao consumidor e receber orientação técnica
3. **Sustentabilidade**: Promove comércio local e agricultura consciente
4. **Inclusão Digital**: Tecnologia de ponta acessível a quem mais precisa

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  HTML5 + CSS3 + JavaScript (Vanilla)                        │
│  - platform.html (Interface principal)                       │
│  - login-new.html (Autenticação)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST (JSON)
                   │ JWT Authentication
┌──────────────────▼──────────────────────────────────────────┐
│                    BACKEND (Java)                            │
│  Spring Boot 3.2 + Spring Security + JWT                    │
│                                                              │
│  Controllers:                                                │
│  ├─ AuthController (Login/Registro)                         │
│  ├─ ConversaController (Chat com IA)                        │
│  └─ MercadoController (Produtos)                            │
│                                                              │
│  Services:                                                   │
│  ├─ AuthService (Autenticação)                              │
│  ├─ IAService (Processamento IA)                            │
│  └─ ConversaService (Gerenciamento Chat)                    │
│                                                              │
│  Repositories (Spring Data JPA):                             │
│  ├─ UsuarioRepository                                        │
│  ├─ ConversaRepository                                       │
│  ├─ MensagemRepository                                       │
│  ├─ ProgressoRepository                                      │
│  └─ ProdutoRepository                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌───────────────┐    ┌────────────────┐
│  H2 Database  │    │  Gemini API    │
│  (Produção:   │    │  (IA)          │
│  PostgreSQL)  │    └────────────────┘
└───────────────┘
```

### Fluxo de Dados

#### 1. Autenticação
```
Usuario → Login Form → POST /api/auth/login
                     → Backend valida credenciais
                     → Gera JWT Token
                     → Frontend armazena token
                     → Redireciona para platform.html
```

#### 2. Chat com IA
```
Usuario digita mensagem → POST /api/conversas/{id}/mensagens
                        → Backend salva mensagem
                        → IAService processa com Gemini
                        → Salva resposta da IA
                        → Retorna para frontend
                        → Exibe no chat
```

#### 3. Mercado
```
Agricultor cadastra produto → POST /api/mercado/produtos
                            → Valida tipo de usuário
                            → Salva no banco
                            → Disponível para compra
```

---

## 🚀 Como Executar

### Pré-requisitos

1. **Java 17+**
   ```bash
   # Verificar versão
   java -version
   
   # Se não tiver, instalar:
   # macOS: brew install openjdk@17
   # Ubuntu: sudo apt install openjdk-17-jdk
   ```

2. **Maven 3.8+**
   ```bash
   # Verificar
   mvn -version
   
   # Instalar:
   # macOS: brew install maven
   # Ubuntu: sudo apt install maven
   ```

3. **API Key do Gemini** (ESSENCIAL para IA funcionar)
   - Acesse: https://makersuite.google.com/app/apikey
   - Crie uma conta Google
   - Gere uma API Key gratuita
   - Copie a chave

### Passo a Passo

#### 1. Configurar Variáveis de Ambiente

**macOS/Linux:**
```bash
cd /Users/wisley/Downloads/Agro_tech-main/backend

# Criar arquivo .env
cp .env.example .env

# Editar e adicionar sua chave
nano .env
# Ou usar qualquer editor
```

No arquivo `.env`, cole sua chave:
```bash
GEMINI_API_KEY=SUA-CHAVE-AQUI
```

**Ou exportar diretamente:**
```bash
export GEMINI_API_KEY="SUA-CHAVE-AQUI"
```

#### 2. Compilar e Executar o Backend

```bash
cd backend

# Dar permissão ao script
chmod +x start.sh

# Executar
./start.sh
```

**OU manualmente:**
```bash
cd backend

# Compilar
mvn clean install

# Executar
mvn spring-boot:run
```

#### 3. Verificar se Backend Está Rodando

Acesse: http://localhost:8080/api

Você deve ver uma página de erro 401 (isso é normal - significa que está funcionando mas precisa autenticação)

#### 4. Abrir o Frontend

**Opção 1: Servidor Python**
```bash
cd /Users/wisley/Downloads/Agro_tech-main/static
python3 -m http.server 3000
```

**Opção 2: Servidor Node.js**
```bash
cd /Users/wisley/Downloads/Agro_tech-main/static
npx serve . -p 3000
```

**Opção 3: Abrir diretamente**
- Abra o arquivo `static/login-new.html` no navegador
- (Pode dar erro de CORS - use uma das opções acima)

#### 5. Acessar a Plataforma

Abra: http://localhost:3000/login-new.html

---

## 📁 Estrutura do Projeto

```
Agro_tech-main/
│
├── backend/                          # Backend Java Spring Boot
│   ├── src/main/
│   │   ├── java/com/agrotech/
│   │   │   ├── config/              # Configurações
│   │   │   │   ├── SecurityConfig.java        # Spring Security + JWT
│   │   │   │   ├── JwtAuthenticationFilter.java
│   │   │   │   └── WebClientConfig.java       # HTTP Client
│   │   │   │
│   │   │   ├── controller/          # Endpoints REST
│   │   │   │   ├── AuthController.java        # /auth/login, /auth/registrar
│   │   │   │   ├── ConversaController.java    # /conversas/*
│   │   │   │   └── MercadoController.java     # /mercado/*
│   │   │   │
│   │   │   ├── dto/                 # Data Transfer Objects
│   │   │   │   ├── RegistroRequest.java
│   │   │   │   ├── LoginRequest.java
│   │   │   │   ├── AuthResponse.java
│   │   │   │   ├── ConversaRequest.java
│   │   │   │   ├── MensagemRequest.java
│   │   │   │   └── IAResponse.java
│   │   │   │
│   │   │   ├── model/               # Entidades JPA
│   │   │   │   ├── Usuario.java     # Estudantes + Agricultores
│   │   │   │   ├── Conversa.java    # Conversas com IA
│   │   │   │   ├── Mensagem.java    # Mensagens individuais
│   │   │   │   ├── Progresso.java   # Progresso dos alunos
│   │   │   │   └── Produto.java     # Produtos do mercado
│   │   │   │
│   │   │   ├── repository/          # Spring Data JPA
│   │   │   │   ├── UsuarioRepository.java
│   │   │   │   ├── ConversaRepository.java
│   │   │   │   ├── MensagemRepository.java
│   │   │   │   ├── ProgressoRepository.java
│   │   │   │   └── ProdutoRepository.java
│   │   │   │
│   │   │   ├── service/             # Lógica de Negócio
│   │   │   │   ├── AuthService.java            # Autenticação
│   │   │   │   ├── JwtService.java             # JWT
│   │   │   │   ├── CustomUserDetailsService.java
│   │   │   │   ├── IAService.java              # ❤️ CORAÇÃO - Integração IA
│   │   │   │   └── ConversaService.java        # Gerenciamento Chat
│   │   │   │
│   │   │   └── AgroTechApplication.java # Main
│   │   │
│   │   └── resources/
│   │       └── application.yml       # Configurações
│   │
│   ├── pom.xml                      # Dependências Maven
│   ├── start.sh                     # Script de inicialização
│   ├── .env.example                 # Exemplo de variáveis
│   └── README.md                    # Documentação
│
└── static/                          # Frontend
    ├── login-new.html               # Login/Registro
    ├── platform.html                # Interface principal
    ├── mercado.html                 # Mercado (existente)
    ├── index.html                   # Página antiga (manter)
    ├── app.js
    ├── auth.js
    └── theme.js
```

---

## 🎓 Funcionalidades Detalhadas

### 1. Sistema de Usuários

**3 Tipos:**
- **ESTUDANTE**: Acesso às 8 IAs educacionais
- **AGRICULTOR**: Acesso a Agro.IA e Mercado
- **ADMIN**: Acesso total (futuro)

**Campos por Tipo:**

Estudante:
- Nome completo, email, username, senha
- Escola, série, idade

Agricultor:
- Nome completo, email, username, senha
- Propriedade, localização, área (hectares)

### 2. IAs Educacionais

Cada IA tem um **prompt especializado** configurado em `IAService.java`:

#### 📖 IA de Português
```
- Gramática (sintaxe, morfologia, ortografia)
- Literatura (autores, obras, movimentos literários)
- Interpretação de texto
- Redação (dissertação, narração, descrição)
```

#### 🔢 IA de Matemática
```
- Aritmética (operações básicas)
- Álgebra (equações, funções)
- Geometria (áreas, volumes)
- Trigonometria
- Cálculo (derivadas, integrais)
```

#### ⚗️ IA de Química
```
- Tabela periódica
- Ligações químicas
- Reações químicas
- Química orgânica
- Estequiometria
```

#### ⚛️ IA de Física
```
- Mecânica (cinemática, dinâmica)
- Termodinâmica
- Eletromagnetismo
- Óptica
- Física moderna
```

#### 🧬 IA de Biologia
```
- Citologia (células)
- Genética
- Evolução
- Ecologia
- Anatomia e fisiologia
```

#### 🌍 IA de Geografia
```
- Geografia física (relevo, clima, hidrografia)
- Geografia humana (população, urbanização)
- Geopolítica
- Economia
- Meio ambiente
```

#### 🏛️ IA de História
```
- História do Brasil
- História mundial
- Civilizações antigas
- Processos históricos
- Análise crítica de eventos
```

#### 🔬 IA de Ciências (Fundamental)
```
- Corpo humano
- Animais e plantas
- Meio ambiente
- Energia
- Matéria
```

### 3. Agro.IA

**Especialista em:**
- Análise de solo (pH, nutrientes, textura)
- Recomendação de cultivos
- Manejo de pragas e doenças
- Técnicas de irrigação
- Agricultura sustentável
- Rotação de culturas
- Adubação orgânica e química

### 4. Mercado Local

**Funcionalidades:**
- Cadastro de produtos
- Categorias: Frutas, Verduras, Legumes, Grãos, Laticínios, Ovos, Mel
- Marcação de produtos orgânicos
- Busca e filtros
- Gestão de estoque
- Contato direto produtor-consumidor

---

## 📡 API Reference

### Autenticação

#### POST /api/auth/registrar
Criar nova conta

**Request:**
```json
{
  "username": "joao123",
  "email": "joao@email.com",
  "senha": "senha123",
  "nomeCompleto": "João da Silva",
  "tipo": "ESTUDANTE",
  "escola": "Escola Municipal",
  "serie": "9º Ano",
  "idade": 14
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzUxMiJ9...",
  "tipo": "Bearer",
  "usuario": {
    "id": 1,
    "username": "joao123",
    "nomeCompleto": "João da Silva",
    "tipo": "ESTUDANTE",
    ...
  }
}
```

#### POST /api/auth/login
Fazer login

**Request:**
```json
{
  "login": "joao123",
  "senha": "senha123"
}
```

### Conversas com IA

#### POST /api/conversas
Criar nova conversa

**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "tipoIA": "MATEMATICA",
  "titulo": "Aprendendo Equações"
}
```

**Response:**
```json
{
  "id": 1,
  "usuario": {...},
  "tipoIA": "MATEMATICA",
  "titulo": "Aprendendo Equações",
  "dataInicio": "2026-03-19T10:00:00",
  "ativa": true
}
```

#### POST /api/conversas/{id}/mensagens
Enviar mensagem

**Request:**
```json
{
  "conteudo": "Como resolver x² + 5x + 6 = 0?"
}
```

**Response:**
```json
{
  "id": 2,
  "remetente": "IA",
  "conteudo": "Vamos resolver essa equação do 2º grau passo a passo...",
  "dataEnvio": "2026-03-19T10:01:00",
  "modelo": "gemini-pro"
}
```

#### GET /api/conversas
Listar conversas do usuário

#### GET /api/conversas/{id}/mensagens
Ver histórico de mensagens

### Mercado

#### GET /api/mercado/produtos
Listar produtos disponíveis

#### POST /api/mercado/produtos
Cadastrar produto (apenas agricultores)

**Request:**
```json
{
  "nome": "Tomate Orgânico",
  "descricao": "Tomate cultivado sem agrotóxicos",
  "categoria": "VERDURAS",
  "preco": 8.50,
  "unidade": "kg",
  "quantidadeDisponivel": 50,
  "organico": true
}
```

#### GET /api/mercado/meus-produtos
Produtos do agricultor logado

---

## 🔧 Troubleshooting

### Problema 1: "GEMINI_API_KEY não configurada"

**Solução:**
```bash
export GEMINI_API_KEY="sua-chave-aqui"
```

Ou adicione no arquivo `.env`

### Problema 2: Erro de CORS no frontend

**Solução:** Use um servidor local:
```bash
cd static
python3 -m http.server 3000
```

### Problema 3: Java não encontrado

**Solução:**
```bash
# macOS
brew install openjdk@17

# Ubuntu/Debian
sudo apt install openjdk-17-jdk
```

### Problema 4: Maven não encontrado

**Solução:**
```bash
# macOS
brew install maven

# Ubuntu/Debian
sudo apt install maven
```

### Problema 5: Porta 8080 em uso

**Solução:** Altere em `application.yml`:
```yaml
server:
  port: 8081
```

E no frontend (login-new.html e platform.html):
```javascript
const API_URL = 'http://localhost:8081/api';
```

### Problema 6: IA não responde

**Verifique:**
1. GEMINI_API_KEY está correta?
2. Tem internet?
3. Verifique logs do backend no terminal

---

## 🌟 Próximos Passos

### Melhorias Planejadas

1. **Upload de Imagens**
   - Fotos de produtos no mercado
   - Análise de imagens de pragas
   - Scan de exercícios

2. **Gamificação**
   - Pontos por estudo
   - Rankings
   - Badges e conquistas
   - Desafios semanais

3. **Chat em Tempo Real**
   - WebSocket
   - Notificações

4. **App Mobile**
   - React Native
   - Offline-first

5. **Análise de Dados**
   - Dashboard de progresso
   - Relatórios de desempenho
   - Analytics para agricultores

---

## 📊 Métricas de Impacto

### Educacional
- ✅ 8 professores virtuais 24/7
- ✅ Adaptação ao nível do aluno
- ✅ Custo zero para estudantes
- ✅ Acesso via celular/PC

### Econômico
- ✅ Conexão direta produtor-consumidor
- ✅ Redução de intermediários
- ✅ Preços mais justos
- ✅ Valorização do produto local

### Social
- ✅ Inclusão digital
- ✅ Democratização do conhecimento
- ✅ Fortalecimento comunitário
- ✅ Desenvolvimento sustentável

---

## 📞 Suporte

### Logs do Backend
```bash
# Ver logs em tempo real
tail -f backend/logs/spring.log
```

### Database Console
Acesse: http://localhost:8080/api/h2-console
- URL: `jdbc:h2:file:./data/agrotech`
- User: `sa`
- Password: (vazio)

---

**Desenvolvido com ❤️ para transformar educação e agricultura no Brasil**

#EducaçãoParaTodos #AgriculturaFamiliar #ImpactoSocial #TecnologiaSocial
