// auth.js - Gerenciamento de autenticação

const API_URL = window.location.origin;

// ── Tipo de usuário selecionado ──────────────────────────────
const TYPE_INFO = {
    produtor:      '🌾 Como <strong>Produtor</strong>, você poderá analisar o solo, postar sua safra e fechar negócios com compradores.',
    comprador:     '🏪 Como <strong>Comprador</strong>, você poderá visualizar safras disponíveis e entrar em contato com produtores. É necessário CNPJ válido.',
    transportador: '🚛 Como <strong>Transportador</strong>, você verá negócios fechados e poderá oferecer frete para escoar a produção.',
};

function selectUserType(type) {
    // Atualiza cards
    document.querySelectorAll('.type-card').forEach(c => c.classList.remove('selected'));
    const card = document.querySelector(`.type-card[data-type="${type}"]`);
    if (card) card.classList.add('selected');

    // Atualiza hidden input
    document.getElementById('selectedUserType').value = type;

    // Info box
    const info = document.getElementById('typeInfo');
    info.innerHTML = TYPE_INFO[type] || '';
    info.classList.add('visible');

    // Ajusta label do nome
    const labelName = document.getElementById('labelName');
    if (type === 'comprador') labelName.textContent = 'Nome do Responsável';
    else if (type === 'transportador') labelName.textContent = 'Seu Nome Completo';
    else labelName.textContent = 'Seu Nome Completo';

    // Mostra/oculta campos extras
    document.getElementById('fieldProdutor').classList.toggle('visible', type === 'produtor');
    document.getElementById('fieldComprador').classList.toggle('visible', type === 'comprador');
    document.getElementById('fieldTransportador').classList.toggle('visible', type === 'transportador');
}

// ── Validação de CNPJ (algoritmo oficial, 100% offline) ───────
function validateCNPJ(cnpj) {
    const n = cnpj.replace(/\D/g, '');
    if (n.length !== 14) return false;
    if (/^(\d)\1+$/.test(n)) return false; // todos iguais

    const calc = (digits, weights) => {
        let sum = 0;
        for (let i = 0; i < weights.length; i++) sum += parseInt(digits[i]) * weights[i];
        const rem = sum % 11;
        return rem < 2 ? 0 : 11 - rem;
    };

    const w1 = [5,4,3,2,9,8,7,6,5,4,3,2];
    const w2 = [6,5,4,3,2,9,8,7,6,5,4,3,2];
    const d1 = calc(n, w1);
    const d2 = calc(n, w2);
    return d1 === parseInt(n[12]) && d2 === parseInt(n[13]);
}

function formatCNPJ(input) {
    let v = input.value.replace(/\D/g, '').slice(0, 14);
    v = v.replace(/^(\d{2})(\d)/, '$1.$2');
    v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
    v = v.replace(/\.(\d{3})(\d)/, '.$1/$2');
    v = v.replace(/(\d{4})(\d)/, '$1-$2');
    input.value = v;
}

function checkCNPJ(input) {
    const status = document.getElementById('cnpjStatus');
    const raw = input.value.replace(/\D/g, '');
    if (!raw) { status.textContent = ''; return; }
    if (validateCNPJ(raw)) {
        status.textContent = '✅ CNPJ válido';
        status.style.color = 'var(--success-text)';
        input.style.borderColor = 'var(--input-focus)';
    } else {
        status.textContent = '❌ CNPJ inválido — verifique os números';
        status.style.color = 'var(--error-text)';
        input.style.borderColor = 'var(--error-text)';
    }
}

// ── Alterna entre abas de login e registro ───────────────────
function showTab(tab) {
    console.log('🔄 Alternando para tab:', tab);
    
    // Remove active de todas as tabs e forms
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form').forEach(f => f.classList.remove('active'));
    
    // Adiciona active na tab correspondente
    if (tab === 'login') {
        document.getElementById('tabLogin').classList.add('active');
    } else {
        document.getElementById('tabRegister').classList.add('active');
    }
    
    // Mostra o form correspondente
    const form = document.getElementById(tab + 'Form');
    if (form) {
        form.classList.add('active');
        console.log('✅ Form ativado:', tab + 'Form');
    }
    
    // Limpa mensagens
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.innerHTML = '';
    }
}

// Inicializar eventos quando o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando eventos...');
    
    // Event listeners para as tabs
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');
    
    if (tabLogin) {
        tabLogin.addEventListener('click', () => showTab('login'));
        console.log('✅ Listener adicionado: tabLogin');
    }
    
    if (tabRegister) {
        tabRegister.addEventListener('click', () => showTab('register'));
        console.log('✅ Listener adicionado: tabRegister');
    }
});

// Exibe mensagens
function showMessage(message, type = 'error') {
    const messageDiv = document.getElementById('message');
    messageDiv.className = type;
    messageDiv.textContent = message;
}

// Salva tokens no localStorage
function saveTokens(accessToken, refreshToken, user) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user', JSON.stringify(user));
}

// Pega token salvo
function getAccessToken() {
    return localStorage.setItem('access_token');
}

// Limpa tokens (logout)
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const btn = document.getElementById('loginBtn');
    
    btn.disabled = true;
    btn.textContent = 'Entrando...';
    
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            saveTokens(data.access_token, data.refresh_token, data.user);
            showMessage('✅ Login realizado! Entrando no sistema...', 'success');
            setTimeout(() => window.location.href = '/app', 1200);
        } else {
            showMessage(data.detail || 'E-mail ou senha incorretos. Tente novamente.');
            btn.disabled = false;
            btn.textContent = 'Entrar';
        }
    } catch (error) {
        showMessage('Não foi possível conectar ao servidor. Verifique sua conexão.');
        btn.disabled = false;
        btn.textContent = 'Entrar';
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    
    const name     = document.getElementById('registerName').value.trim();
    const email    = document.getElementById('registerEmail').value.trim();
    const phone    = document.getElementById('registerPhone').value.trim();
    const password = document.getElementById('registerPassword').value;
    const userType = document.getElementById('selectedUserType').value;
    const btn      = document.getElementById('registerBtn');

    // Campos por tipo
    const farmName    = document.getElementById('registerFarm')?.value.trim() || null;
    const companyName = document.getElementById('registerCompany')?.value.trim() || null;
    const cnpjRaw     = document.getElementById('registerCNPJ')?.value.replace(/\D/g, '') || null;
    const vehicle     = document.getElementById('registerVehicle')?.value || null;

    // Município e estado conforme tipo
    const cityMap  = { produtor: 'registerCityP', comprador: 'registerCityC', transportador: 'registerCityT' };
    const stateMap = { produtor: 'registerStateP', comprador: 'registerStateC', transportador: 'registerStateT' };
    const city  = document.getElementById(cityMap[userType])?.value.trim() || null;
    const state = document.getElementById(stateMap[userType])?.value || null;

    // Validações básicas
    if (!name)  { showMessage('Por favor, informe seu nome completo.'); return; }
    if (!email) { showMessage('Por favor, informe seu e-mail.'); return; }
    if (password.length < 6) { showMessage('A senha deve ter pelo menos 6 caracteres.'); return; }
    if (password.length > 72) { showMessage('A senha deve ter no máximo 72 caracteres.'); return; }

    // Validação CNPJ para comprador
    if (userType === 'comprador') {
        if (!cnpjRaw) { showMessage('Informe o CNPJ da empresa.'); return; }
        if (!validateCNPJ(cnpjRaw)) { showMessage('O CNPJ informado não é válido. Verifique os números.'); return; }
        if (!companyName) { showMessage('Informe o nome da empresa.'); return; }
    }

    btn.disabled = true;
    btn.textContent = 'Criando conta...';
    
    try {
        const body = {
            name,
            email,
            phone: phone || null,
            password,
            user_type: userType,
            farm_name: farmName,
            company_name: companyName,
            cnpj: cnpjRaw || null,
            city,
            state,
            vehicle_type: vehicle || null,
        };

        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Conta criada! Vai para aba de login com email preenchido
            showMessage('✅ Conta criada com sucesso! Agora faça seu login.', 'success');
            btn.textContent = 'Conta Criada!';
            setTimeout(() => {
                showTab('login');
                const loginEmail = document.getElementById('loginEmail');
                if (loginEmail) loginEmail.value = email;
                showMessage('✅ Conta criada! Entre com seu e-mail e senha.', 'success');
            }, 1200);
        } else {
            showMessage(data.detail || 'Erro ao criar conta. Tente novamente.');
            btn.disabled = false;
            btn.textContent = 'Criar Conta';
        }
    } catch (error) {
        showMessage('Não foi possível conectar ao servidor. Verifique sua conexão.');
        btn.disabled = false;
        btn.textContent = 'Criar Conta';
    }
}

// Função auxiliar para fazer requests autenticadas
async function authenticatedFetch(url, options = {}) {
    const token = getAccessToken();
    
    if (!token) {
        throw new Error('Não autenticado');
    }
    
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, options);
    
    // Se token expirou, tentar renovar
    if (response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
            const refreshResponse = await fetch(`${API_URL}/api/auth/refresh`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({refresh_token: refreshToken})
            });
            
            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                saveTokens(data.access_token, data.refresh_token, data.user);
                
                // Repetir request original com novo token
                options.headers['Authorization'] = `Bearer ${data.access_token}`;
                return fetch(url, options);
            }
        }
        
        // Se não conseguiu renovar, redirecionar para login
        clearTokens();
        window.location.href = '/login.html';
    }
    
    return response;
}
