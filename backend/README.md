# 🌱 AgroTech Platform - Plataforma de Ensino e Agronegócio

## 📚 Sobre o Projeto

A **AgroTech Platform** é uma plataforma completa que integra:

### 🎓 Sistema Educacional com IA
- **IA de Português** - Professor virtual de gramática, literatura e redação
- **IA de Matemática** - Ensino de aritmética, álgebra, geometria e cálculo
- **IA de Química** - Química orgânica, inorgânica e análises
- **IA de Física** - Mecânica, termodinâmica e eletromagnetismo
- **IA de Biologia** - Genética, ecologia e anatomia
- **IA de Geografia** - Geografia física e humana
- **IA de História** - História do Brasil e mundial
- **IA de Ciências** - Ciências naturais para fundamental

### 🌾 Agro.IA para Agricultores
- Análise de solo
- Recomendações de cultivo
- Prevenção de pragas
- Técnicas de irrigação
- Agricultura sustentável

### 🛒 Mercado Local
- Venda de produtos agrícolas
- Conexão direta produtor-consumidor
- Incentivo ao comércio local
- Produtos orgânicos certificados

## 🏗️ Arquitetura

### Backend (Java Spring Boot)
```
backend/
├── src/main/java/com/agrotech/
│   ├── config/          # Configurações (Security, CORS, WebClient)
│   ├── controller/      # Endpoints REST
│   ├── dto/            # Data Transfer Objects
│   ├── model/          # Entidades JPA
│   ├── repository/     # Repositórios Spring Data
│   └── service/        # Lógica de negócio
├── src/main/resources/
│   └── application.yml # Configurações da aplicação
└── pom.xml            # Dependências Maven
```

### Frontend (HTML/JS)
```
static/
├── index.html         # Página principal
├── login.html         # Login/Registro
├── app.js            # Lógica principal
├── auth.js           # Autenticação
└── theme.js          # Tema dark/light
```

## 🚀 Como Executar

### Pré-requisitos
- Java 17 ou superior
- Maven 3.8+
- API Key do Google Gemini (ou Ollama local)

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` ou configure as variáveis:

```bash
# API do Gemini (obrigatório para usar IA)
export GEMINI_API_KEY="sua-chave-api-aqui"

# Opcional: para usar Ollama local
export OLLAMA_BASE_URL="http://localhost:11434"
```

Para obter uma chave do Gemini:
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma nova API Key
3. Cole no `.env`

### 2. Executar o Backend

```bash
cd backend

# Compilar o projeto
mvn clean install

# Executar a aplicação
mvn spring-boot:run
```

O servidor estará rodando em: `http://localhost:8080/api`

### 3. Acessar o Frontend

Abra o arquivo `static/index.html` em um navegador ou use um servidor local:

```bash
# Usando Python
cd static
python3 -m http.server 3000

# Ou usando Node.js
npx serve static -p 3000
```

Acesse: `http://localhost:3000`

## 📱 Usando a Plataforma

### Para Estudantes

1. **Registrar-se**
   - Clique em "Registrar"
   - Selecione tipo: "Estudante"
   - Preencha: nome, escola, série, idade
   - Faça login

2. **Estudar com IA**
   - Escolha uma matéria (Português, Matemática, etc)
   - Comece uma nova conversa
   - Faça perguntas, peça explicações
   - A IA se adapta ao seu nível

3. **Acompanhar Progresso**
   - Veja seu histórico de estudos
   - Métricas de desempenho
   - Tópicos estudados

### Para Agricultores

1. **Registrar-se**
   - Selecione tipo: "Agricultor"
   - Informe: propriedade, localização, área

2. **Usar Agro.IA**
   - Faça perguntas sobre cultivo
   - Envie fotos de pragas (futuro)
   - Receba recomendações personalizadas

3. **Vender no Mercado**
   - Cadastre seus produtos
   - Defina preço e quantidade
   - Gerencie estoque
   - Marque produtos orgânicos

### Para Consumidores

1. **Explorar Mercado**
   - Veja produtos disponíveis
   - Filtre por categoria
   - Busque produtos orgânicos
   - Encontre produtores locais

## 🔧 API Endpoints

### Autenticação
- `POST /api/auth/registrar` - Criar conta
- `POST /api/auth/login` - Fazer login

### Conversas com IA
- `POST /api/conversas` - Nova conversa
- `POST /api/conversas/{id}/mensagens` - Enviar mensagem
- `GET /api/conversas` - Listar conversas
- `GET /api/conversas/{id}/mensagens` - Ver histórico

### Mercado
- `GET /api/mercado/produtos` - Listar produtos
- `POST /api/mercado/produtos` - Cadastrar produto
- `GET /api/mercado/meus-produtos` - Meus produtos
- `PUT /api/mercado/produtos/{id}` - Atualizar produto

## 🎨 Tipos de IA Disponíveis

```java
public enum TipoIA {
    // IAs Educacionais
    PORTUGUES,
    MATEMATICA,
    QUIMICA,
    FISICA,
    BIOLOGIA,
    GEOGRAFIA,
    HISTORIA,
    CIENCIAS,
    
    // IA Agrícola
    AGRO_IA,
    
    // IA do Mercado
    ASSISTENTE_MERCADO
}
```

## 🗄️ Banco de Dados

O projeto usa **H2 Database** em modo arquivo:
- Dados salvos em: `./data/agrotech.mv.db`
- Console H2: `http://localhost:8080/api/h2-console`
- URL JDBC: `jdbc:h2:file:./data/agrotech`
- User: `sa`
- Password: (vazio)

### Para usar PostgreSQL em Produção

Altere `application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/agrotech
    username: postgres
    password: sua-senha
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

## 🔒 Segurança

- **Autenticação JWT** - Token Bearer
- **BCrypt** para senhas
- **CORS** configurado
- **Session Stateless**
- **Validação** de inputs

## 🌟 Funcionalidades Futuras

- [ ] Upload de fotos de produtos
- [ ] Chat em tempo real com WebSocket
- [ ] Sistema de avaliações
- [ ] Gamificação para estudantes
- [ ] Certificados de conclusão
- [ ] App mobile (React Native)
- [ ] Integração com pagamento
- [ ] Análise de imagens (pragas, solo)

## 📊 Tecnologias

### Backend
- Java 17
- Spring Boot 3.2
- Spring Security + JWT
- Spring Data JPA
- H2 Database
- WebFlux (HTTP Client)
- Lombok
- Maven

### Frontend
- HTML5 / CSS3
- JavaScript (Vanilla)
- Fetch API
- LocalStorage

### IA
- Google Gemini API
- Ollama (opcional)

## 🤝 Contribuindo

Este projeto visa democratizar o acesso à educação e fortalecer a agricultura familiar.

## 📄 Licença

MIT License - Use livremente para educação e desenvolvimento social.

## 👨‍💻 Autor

Desenvolvido com ❤️ para ajudar estudantes e agricultores.

---

**#EducaçãoParaTodos #AgriculturaFamiliar #IA #ImpactoSocial**
