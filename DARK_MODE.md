# 🌙 Dark Mode - VitaGreen

## Visão Geral

O **VitaGreen** agora possui **modo escuro (dark mode)** completo com:
- ✅ Alternância automática entre tema claro e escuro
- ✅ Detecção de preferência do sistema
- ✅ Persistência da escolha do usuário (localStorage)
- ✅ Transições suaves entre temas
- ✅ Botão de alternância em todas as páginas

---

## 🎨 Temas Disponíveis

### Tema Claro (Light Mode)
- **Fundo principal:** Branco/Cinza claro (#FAFBFC)
- **Superfícies:** Branco puro (#FFFFFF)
- **Texto:** Preto/Cinza escuro (#111827)
- **Primário:** Verde escuro (#0D5C2E)
- **Acento:** Verde claro (#22C55E)

### Tema Escuro (Dark Mode)
- **Fundo principal:** Preto/Cinza muito escuro (#0F1419)
- **Superfícies:** Cinza escuro (#1A1F29)
- **Texto:** Branco/Cinza claro (#F9FAFB)
- **Primário:** Verde claro (#22C55E)
- **Acento:** Verde brilhante (#4ADE80)

---

## 🛠️ Implementação Técnica

### 1. Variáveis CSS

Todas as cores usam **CSS Custom Properties** (variáveis):

```css
:root[data-theme="light"] {
    --primary: #0D5C2E;
    --bg: #FAFBFC;
    --surface: #FFFFFF;
    --text: #111827;
    /* ... outras variáveis ... */
}

:root[data-theme="dark"] {
    --primary: #22C55E;
    --bg: #0F1419;
    --surface: #1A1F29;
    --text: #F9FAFB;
    /* ... outras variáveis ... */
}
```

### 2. JavaScript de Controle

O arquivo **`theme.js`** gerencia:

```javascript
// Carregar tema salvo ou preferência do sistema
function loadTheme() {
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches 
        ? 'dark' : 'light';
}

// Aplicar tema
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateToggleButton(theme);
}

// Alternar tema
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    setTheme(current === 'light' ? 'dark' : 'light');
}
```

### 3. Botão de Alternância

```html
<button id="themeToggle" class="theme-toggle" aria-label="Alternar tema">
    🌙
</button>
```

- **Ícone:** 🌙 (lua) no modo claro → ☀️ (sol) no modo escuro
- **Posição:** Fixo no canto superior direito
- **Animação:** Rotação ao passar o mouse

---

## 📱 Uso

### Para o Usuário

1. **Alternância Manual:**
   - Clique no botão 🌙/☀️ no canto superior direito
   - O tema muda instantaneamente
   - Sua preferência é salva automaticamente

2. **Preferência do Sistema:**
   - Se você nunca escolheu um tema, o sistema usa a preferência do seu dispositivo
   - Exemplo: Se seu celular/computador está em dark mode, o site inicia em dark mode

3. **Persistência:**
   - Sua escolha fica salva mesmo se você fechar o navegador
   - Na próxima visita, o tema escolhido será mantido

### Para Desenvolvedores

#### Adicionar Dark Mode em Nova Página

1. **No CSS:**
```css
:root[data-theme="light"] {
    --minha-cor: #000000;
}

:root[data-theme="dark"] {
    --minha-cor: #FFFFFF;
}

.meu-elemento {
    color: var(--minha-cor);
}
```

2. **No HTML:**
```html
<button id="themeToggle" class="theme-toggle">🌙</button>
<script src="theme.js"></script>
```

#### Variáveis Disponíveis

| Variável | Uso | Light | Dark |
|----------|-----|-------|------|
| `--primary` | Cor principal (botões, links) | #0D5C2E | #22C55E |
| `--bg` | Fundo da página | #FAFBFC | #0F1419 |
| `--surface` | Cartões, painéis | #FFFFFF | #1A1F29 |
| `--text` | Texto principal | #111827 | #F9FAFB |
| `--text-secondary` | Texto secundário | #6B7280 | #D1D5DB |
| `--text-muted` | Texto desabilitado | #9CA3AF | #9CA3AF |
| `--border` | Bordas | #E5E7EB | #2D3748 |
| `--shadow` | Sombras | rgba(0,0,0,0.04) | rgba(0,0,0,0.3) |

---

## 🎯 Benefícios

### Para Agricultores
- ✅ **Menos cansaço visual** ao usar em ambientes escuros (noite, galpões)
- ✅ **Economia de bateria** em celulares com tela OLED/AMOLED
- ✅ **Melhor legibilidade** conforme preferência pessoal

### Para o Sistema
- ✅ **Profissionalismo** - Sistema moderno e completo
- ✅ **Acessibilidade** - Atende preferências visuais
- ✅ **Experiência consistente** - Funciona em login.html e index.html

---

## 🔧 Arquivos Modificados

### Criados
- ✅ `static/theme.js` - Gerenciador de temas

### Atualizados
- ✅ `static/login.html` - Dark mode + botão toggle
- ✅ `static/index.html` - Dark mode + botão toggle

---

## 🧪 Como Testar

1. **Abrir o sistema:**
   ```bash
   cd /Users/wisley/Downloads/VitaGreenProjeto
   python main.py
   ```

2. **Acessar no navegador:**
   - http://localhost:8000 (página principal)
   - http://localhost:8000/login.html (página de login)

3. **Testar alternância:**
   - Clique no botão 🌙/☀️ no canto superior direito
   - Verifique se todas as cores mudam suavemente
   - Recarregue a página (F5) - o tema deve permanecer

4. **Testar preferência do sistema:**
   - Limpe o localStorage: Abra o Console do navegador (F12) e digite:
     ```javascript
     localStorage.removeItem('theme');
     location.reload();
     ```
   - Mude a preferência do sistema (Configurações > Tema escuro/claro)
   - Recarregue o site - deve seguir a preferência do sistema

---

## 🎨 Capturas de Tela

### Modo Claro
- Fundo branco/cinza claro
- Verde escuro nos botões (#0D5C2E)
- Texto preto (#111827)

### Modo Escuro
- Fundo preto/cinza muito escuro (#0F1419)
- Verde claro nos botões (#22C55E)
- Texto branco (#F9FAFB)

---

## 📊 Detalhes Técnicos

### localStorage
```javascript
// Salvar tema
localStorage.setItem('theme', 'dark');

// Carregar tema
const theme = localStorage.getItem('theme');

// Limpar tema
localStorage.removeItem('theme');
```

### Detecção de Preferência do Sistema
```javascript
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
```

### Listener de Mudanças no Sistema
```javascript
window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
```

---

## ✅ Checklist de Implementação

- [x] Criar `theme.js` com funções de alternância
- [x] Adicionar variáveis CSS para light mode
- [x] Adicionar variáveis CSS para dark mode
- [x] Adicionar botão toggle em `login.html`
- [x] Adicionar botão toggle em `index.html`
- [x] Testar persistência no localStorage
- [x] Testar detecção de preferência do sistema
- [x] Adicionar transições suaves
- [x] Garantir contraste adequado
- [x] Documentar implementação

---

## 🚀 Próximos Passos (Opcional)

- [ ] Adicionar mais temas (alto contraste, daltônico)
- [ ] Criar menu de configuração de aparência
- [ ] Adicionar animações personalizadas
- [ ] Implementar tema automático baseado no horário

---

## 📝 Notas Importantes

1. **Compatibilidade:** Funciona em todos os navegadores modernos (Chrome, Firefox, Safari, Edge)
2. **Performance:** Transições leves (0.3s) não afetam desempenho
3. **SEO:** Atributo `data-theme` não afeta indexação
4. **Acessibilidade:** `aria-label="Alternar tema"` para leitores de tela

---

**Desenvolvido para o VitaGreen** 🌱
*Sistema completo com IA local (Ollama), autenticação JWT e agora Dark Mode!*
