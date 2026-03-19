// app.js - JavaScript para AgriSensi

const API_URL = window.location.origin;
let currentSessionId = null;

// Analisa o solo
async function analyzeSoil() {
    const ph = parseFloat(document.getElementById('ph').value);
    const humidity = parseFloat(document.getElementById('humidity').value);
    const nitrogen = parseFloat(document.getElementById('nitrogen').value) || null;
    const phosphorus = parseFloat(document.getElementById('phosphorus').value) || null;
    const potassium = parseFloat(document.getElementById('potassium').value) || null;
    const crop = document.getElementById('crop').value || null;

    if (!ph || !humidity) {
        alert('Por favor, preencha pelo menos pH e Umidade');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/api/analyze`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ph, humidity, nitrogen, phosphorus, potassium, crop})
        });

        const result = await response.json();

        if (result.success) {
            showResult(result.analysis);
        } else {
            alert('Erro: ' + (result.error || 'Algo deu errado'));
        }
    } catch (error) {
        alert('Erro ao conectar com o servidor: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Inicia chat
async function startChat() {
    const ph = parseFloat(document.getElementById('chat-ph').value) || null;
    const humidity = parseFloat(document.getElementById('chat-humidity').value) || null;

    showLoading(true, 'chat');

    try {
        const response = await fetch(`${API_URL}/api/conversation/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ph, humidity})
        });

        const result = await response.json();

        if (result.success) {
            currentSessionId = result.session_id;
            addMessage('assistant', result.message);
            document.getElementById('chat-start').style.display = 'none';
            document.getElementById('chat-conversation').style.display = 'block';
        }
    } catch (error) {
        alert('Erro: ' + error.message);
    } finally {
        showLoading(false, 'chat');
    }
}

// Envia mensagem
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    addMessage('user', message);
    input.value = '';

    showLoading(true, 'chat');

    try {
        const response = await fetch(`${API_URL}/api/conversation/message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        const result = await response.json();

        if (result.success) {
            addMessage('assistant', result.message);
        }
    } catch (error) {
        alert('Erro: ' + error.message);
    } finally {
        showLoading(false, 'chat');
    }
}

// Adiciona mensagem no chat
function addMessage(role, text) {
    const messagesDiv = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${role}`;
    msgDiv.textContent = text;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Mostra/esconde loading
function showLoading(show, section = 'analysis') {
    const btnId = section === 'chat' ? 'btn-send' : 'btn-analyze';
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = show;
        btn.textContent = show ? 'Processando...' : (section === 'chat' ? 'Enviar' : 'Analisar Solo');
    }
}

// Mostra resultado
function showResult(analysis) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <div class="result-box">
            <h3>📊 Análise do seu Solo</h3>
            <p>${analysis}</p>
            <small>💡 Análise feita com IA local - 100% gratuita</small>
        </div>
    `;
    resultDiv.style.display = 'block';
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});
