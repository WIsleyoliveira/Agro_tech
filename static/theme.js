// theme.js - Gerenciador de Dark Mode

// Carrega tema salvo ou detecta preferência do sistema
function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    console.log('🎨 Carregando tema:', theme);
    setTheme(theme);
}

// Define o tema
function setTheme(theme) {
    console.log('✨ Aplicando tema:', theme);
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Atualizar ícone do botão se existir
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            // Font Awesome icons
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        } else {
            // Fallback para emoji se não tiver ícone
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
        themeToggle.setAttribute('aria-label', 
            theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'
        );
    }
    console.log('✅ Tema aplicado! data-theme:', document.documentElement.getAttribute('data-theme'));
}

// Alterna entre temas
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    console.log('🔄 Alternando tema:', currentTheme, '→', newTheme);
    setTheme(newTheme);
}

// Inicializar ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Theme.js carregado!');
    loadTheme();
    
    // Adicionar listener ao botão de tema
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        console.log('✅ Listener adicionado ao botão de tema');
    } else {
        console.warn('⚠️ Botão themeToggle não encontrado!');
    }
});

// Detectar mudanças na preferência do sistema
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});
