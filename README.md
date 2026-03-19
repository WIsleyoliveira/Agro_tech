# 🌱 AgroTech Platform

> Plataforma completa de **educação com IA** para estudantes e **agronegócio digital** para agricultores. Tutores inteligentes para cada matéria escolar, consultor agrônomo com IA, e mercado local conectando produtores, compradores e transportadores.

---

## Visão Geral

| Perfil | O que acessa |
|--------|-------------|
| 🎓 **Estudante** | Tutores de IA para Português, Matemática, Física, Química, Biologia, Geografia, História e Ciências |
| 🌾 **Agricultor** | Agro.IA (consultor agrônomo), Mercado Local e Assistente de Vendas |

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | Java 21 + Spring Boot 3.2 |
| Banco de dados | H2 (arquivo local) via JPA/Hibernate |
| IA / Chat | Ollama (`llama3.2:3b`) — 100% offline |
| Autenticação | JWT (Spring Security) com BCrypt |
| Frontend | HTML + CSS + JavaScript puro |
| Estilo | Inter / DM Sans, Font Awesome 6, CSS Variables |
| Tema | Dark/Light mode |

---

## Pré-requisitos

- **Java 21** — [Adoptium Temurin](https://adoptium.net/)
- **Maven 3.8+**
- **Ollama** com o modelo `llama3.2:3b`

```bash
# Instalar Ollama (macOS)
brew install ollama

# Baixar o modelo de IA
ollama pull llama3.2:3b

# Iniciar Ollama em background
ollama serve
```

---

## Instalação e Execução

```bash
# 1. Clonar o repositório
git clone https://github.com/WIsleyoliveira/Agro_tech.git
cd Agro_tech

# 2. Compilar o backend
cd backend
mvn clean package -DskipTests

# 3. Iniciar o backend (porta 8080)
java -jar target/agrotech-platform-1.0.0.jar

# 4. Em outro terminal, servir o frontend (porta 3000)
cd ../static
python3 -m http.server 3000

# 5. Acessar no navegador
open http://localhost:3000/login-new.html
```

---

## Uso Rápido

### Criar conta
1. Acesse `http://localhost:3000/login-new.html`
2. Clique em **"Criar conta"**
3. Escolha o tipo: **Estudante** ou **Agricultor**
4. Após o cadastro, você é redirecionado automaticamente:
   - **Estudante** → `platform.html` (tutores educacionais)
   - **Agricultor** → `mercado.html` (mercado + Agro.IA)

---

## Funcionalidades

### 🎓 Plataforma Educacional (`platform.html`)

Tutores de IA especializados com respostas didáticas, estruturadas e contextualizadas:

| Tutor | Cobertura |
|-------|-----------|
| 📝 Português | Gramática, literatura, redação, interpretação |
| ➕ Matemática | Aritmética, álgebra, geometria, cálculo |
| ⚗️ Química | Geral, orgânica, inorgânica, estequiometria |
| ⚡ Física | Mecânica, termodinâmica, eletromagnetismo, óptica |
| 🧬 Biologia | Citologia, genética, ecologia, fisiologia |
| 🌍 Geografia | Física, humana, geopolítica, ambiental |
| 📖 História | Brasil, geral, pré-história |
| 🔬 Ciências | Corpo humano, natureza, astronomia |

Cada tutor segue um estilo de resposta aprimorado:
- Explica passo a passo com raciocínio explícito
- Usa analogias e exemplos do cotidiano
- Adapta a linguagem ao nível do aluno
- Formata respostas com títulos, listas e destaques

### 🌾 Módulo Agrícola

**Agro.IA** — consultor agrônomo com IA:
- Análise de solo, pragas, doenças, adubação e irrigação
- Orientações para agricultura familiar e sustentável
- Respostas técnicas com linguagem acessível

**Mercado Local** — conecta produtores, compradores e transportadores:
- Vitrine de anúncios com filtros
- Sistema de negociações com fluxo de status
- Chat por negócio
- Sistema de avaliações por estrelas
- Notificações automáticas
- Compartilhamento de anúncios
- Perfil público do produtor

---

## Estrutura do Projeto

```
Agro_tech/
├── backend/                          # Spring Boot API
│   ├── pom.xml
│   └── src/main/java/com/agrotech/
│       ├── AgroTechApplication.java
│       ├── config/
│       │   ├── SecurityConfig.java        # JWT + CORS
│       │   ├── JwtAuthenticationFilter.java
│       │   └── WebClientConfig.java
│       ├── controller/
│       │   ├── AuthController.java        # /auth/login, /auth/registrar
│       │   ├── ConversaController.java    # /conversas
│       │   └── MercadoController.java     # /mercado
│       ├── service/
│       │   ├── IAService.java             # Integração Ollama + Gemini
│       │   ├── ConversaService.java
│       │   ├── AuthService.java
│       │   └── JwtService.java
│       ├── model/                         # Entidades JPA
│       └── repository/                    # Spring Data JPA
├── static/                           # Frontend HTML/CSS/JS
│   ├── login-new.html                # Login e registro
│   ├── platform.html                 # Tutores educacionais (estudantes)
│   ├── mercado.html                  # Mercado local (agricultores)
│   └── index.html                    # Análise de solo
└── README.md
```

---

## Rotas da API

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/registrar` | Cadastrar novo usuário |
| POST | `/auth/login` | Login — retorna JWT |

### Conversas com IA
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/conversas` | Criar nova conversa |
| GET | `/conversas` | Listar conversas do usuário |
| POST | `/conversas/{id}/mensagens` | Enviar mensagem (aciona IA) |
| GET | `/conversas/{id}/mensagens` | Histórico de mensagens |
| DELETE | `/conversas/{id}` | Arquivar conversa |

### Mercado
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/mercado/produtos` | Listar produtos |
| POST | `/mercado/produtos` | Publicar produto |

---

## Configuração da IA

As configurações ficam em `backend/src/main/resources/application.yml`:

```yaml
ai:
  ollama:
    base-url: http://localhost:11434   # URL do Ollama
    enabled: true
  gemini:
    api-key: ${GEMINI_API_KEY:}        # Opcional: chave da API Gemini
    enabled: false
```

Para usar o **Gemini** em vez do Ollama:
```yaml
ai:
  gemini:
    api-key: SUA_CHAVE_AQUI
    enabled: true
  ollama:
    enabled: false
```

---

## Problemas Comuns

**Ollama não está respondendo**
```bash
ollama serve
ollama list   # Verificar se llama3.2:3b está instalado
```

**Modelo não encontrado**
```bash
ollama pull llama3.2:3b
```

**Porta 8080 em uso**
```bash
lsof -i :8080
kill -9 <PID>
```

**Token expirado no frontend**
- Faça logout e login novamente
- O token JWT expira em 24 horas

---

## Observações Técnicas

- **100% offline:** A IA (Ollama) roda localmente — nenhum dado sai da sua máquina
- **Banco embarcado:** H2 salvo em `backend/data/agrotech.mv.db`, zero configuração extra
- **Respostas da IA:** podem levar 20–40 segundos com `llama3.2:3b` em hardware comum
- **Dark/Light mode:** Alternância salva no `localStorage`
- **Mobile-friendly:** Layout responsivo

---

## Licença

MIT

> Plataforma completa para o agronegócio: **Mercado Local** conectando produtores, compradores e transportadores, mais **Análise de Solo** com IA agronômica 100% offline.

---

