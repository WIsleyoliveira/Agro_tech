import google.generativeai as genai
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from google.generativeai.types import GenerationConfig  # <-- NOVO IMPORT


class GeminiAgricultureService:
    def __init__(self):
        print("🌱 Iniciando serviço Gemini IA (Unificado)...")
        self.api_key = self._load_api_key()

        if not self.api_key or "sua_chave" in self.api_key:
            print("❌ ERRO: Configure sua chave no arquivo .env")
            raise ValueError("Chave da API não configurada")

        genai.configure(api_key=self.api_key)
        # MODELO PRINCIPAL
        self.model_name = 'gemini-flash-latest'  # Atualizado para modelo mais recente
        self.model = genai.GenerativeModel(self.model_name)

        # Configurações de geração por tipo de uso
        self.config_analysis = GenerationConfig(
            max_output_tokens=500,  # Espaço para análise completa sem corte
            temperature=0.7,         # Mais determinístico para recomendações técnicas
            top_p=0.9,
            ##top_k=40
        )
        self.config_conversation = GenerationConfig(
            max_output_tokens=500,  # Mesmo teto da análise para não cortar respostas
            temperature=0.7,
            top_p=0.9,
            ## top_k=40
        )

        # Histórico para sessões conversacionais
        self.sessions: Dict[str, List[Dict]] = {}
        self.call_count = 0
        self.total_estimated_cost = 0.0

        print(f"✅ Serviço configurado. Modelo: {self.model_name}")
        print(
            f"   Análise: {self.config_analysis.max_output_tokens} tokens | Chat: {self.config_conversation.max_output_tokens} tokens")
        print("   Módulos: Análise completa (8 parâmetros) + Conversacional")
        print("   Endpoints: /api/analyze, /api/analyze/quick, /api/conversation/*")

    def _load_api_key(self):
        """Carrega a chave API do arquivo .env ou variável de ambiente"""
        # Primeiro tenta variável de ambiente
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print(f"🔑 Chave carregada do ambiente: {api_key[:10]}...")
            return api_key

        # Depois tenta arquivo .env
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('GEMINI_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        key = key.replace('"', '').replace("'", "")
                        print(f"🔑 Chave carregada do .env: {key[:10]}...")
                        return key
        except Exception as e:
            print(f"⚠️  Erro ao ler .env: {e}")
        return None

    def _log_api_call(self, prompt: str, response_text: str):
        """Registra cada chamada à API com custo estimado"""
        self.call_count += 1

        # Estimativa de tokens (aproximada)
        input_tokens_approx = len(prompt.split()) * 1.3
        output_tokens_approx = len(response_text.split()) * 1.3

        # Custo estimado (baseado no modelo Gemini Flash)
        # Preços por 1000 tokens: entrada $0.00025, saída $0.0005
        call_cost = (input_tokens_approx / 1000 * 0.00025) + \
            (output_tokens_approx / 1000 * 0.0005)
        self.total_estimated_cost += call_cost

        log_entry = {
            "call_number": self.call_count,
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "input_tokens_approx": round(input_tokens_approx),
            "output_tokens_approx": round(output_tokens_approx),
            "cost_this_call_usd": round(call_cost, 6),
            "total_cost_usd": round(self.total_estimated_cost, 6),
            "prompt_preview": prompt[:150] + "..." if len(prompt) > 150 else prompt
        }

        print(f"\n{'='*60}")
        print(
            f"🚀 CHAMADA #{self.call_count} - {log_entry['timestamp'].split('T')[1][:8]}")
        print(f"   Modelo: {self.model_name}")
        print(
            f"   Tokens: {log_entry['input_tokens_approx']} in / {log_entry['output_tokens_approx']} out")
        print(f"   Custo desta chamada: ${call_cost:.6f}")
        print(f"   Custo acumulado: ${self.total_estimated_cost:.6f}")
        print(f"{'='*60}\n")

        # Salva log em arquivo
        os.makedirs('logs', exist_ok=True)
        log_file = f"logs/api_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️  Erro ao salvar log: {e}")

        return log_entry

    # ===================== ANÁLISE COMPLETA (8 PARÂMETROS) =====================
    def analyze_soil_complete(self, soil_params: Dict):
        """Análise completa com 8 parâmetros do solo"""
        try:
            # Extrai parâmetros com valores padrão
            ph = soil_params.get('ph', 0)
            humidity = soil_params.get('humidity', 0)
            nitrogen = soil_params.get('nitrogen')
            phosphorus = soil_params.get('phosphorus')
            potassium = soil_params.get('potassium')
            calcium = soil_params.get('calcium')
            magnesium = soil_params.get('magnesium')
            organic_matter = soil_params.get('organic_matter')
            crop = soil_params.get('crop', 'geral')

            # Conta quantos parâmetros foram fornecidos
            provided_params = sum(1 for value in [ph, humidity, nitrogen, phosphorus,
                                                  potassium, calcium, magnesium, organic_matter]
                                  if value is not None)

            prompt_lines = [
                "Você é um consultor agronômico sênior da EMBRAPA. Forneça uma análise técnica completa e bem desenvolvida para estes parâmetros de solo:",
                f"\n## DADOS DO SOLO ANALISADO:",
                f"- pH: {ph} (escala 0-14)",
                f"- Umidade: {humidity}%"
            ]

            if nitrogen is not None:
                prompt_lines.append(
                    f"- Nitrogênio (N): {nitrogen} kg/ha (convertido de sensor mg/kg)")
            if phosphorus is not None:
                prompt_lines.append(
                    f"- Fósforo (P): {phosphorus} kg/ha (convertido de sensor mg/kg)")
            if potassium is not None:
                prompt_lines.append(
                    f"- Potássio (K): {potassium} kg/ha (convertido de sensor mg/kg)")
            if calcium is not None:
                prompt_lines.append(f"- Cálcio (Ca): {calcium} cmolc/dm³")
            if magnesium is not None:
                prompt_lines.append(f"- Magnésio (Mg): {magnesium} cmolc/dm³")
            if organic_matter is not None:
                prompt_lines.append(
                    f"- Matéria Orgânica (MO): {organic_matter} g/dm³")

            if crop and crop != 'geral':
                prompt_lines.append(f"\n## CULTURA ALVO: {crop.upper()}")

            prompt_lines.extend([
                "",
                "## FORMATO (siga todas as seções):",
                "",
                "### 1. DIAGNÓSTICO",
                "Classifique o solo (Ótimo / Regular / Crítico). Interprete cada parâmetro fora da faixa ideal, explicando o impacto na cultura.",
                "",
                "### 2. CORREÇÕES PRIORITÁRIAS",
                "Liste 2 a 4 ações com: produto, dose específica (ex: 2.5 t/ha de calcário dolomítico), época de aplicação e justificativa breve.",
                "",
                "### 3. MANEJO (próximos 3 meses)",
                "Descreva 2-3 práticas de manejo recomendadas e como monitorar a evolução do solo.",
                "",
                "### 4. RESUMO",
                "Encerre com um parágrafo curto resumindo o estado geral do solo e as ações mais urgentes.",
                "",
                "## REGRAS:",
                "- Base técnica EMBRAPA. Dados numéricos nas correções.",
                "- Recomende apenas o que os dados indicam. Não invente parâmetros ausentes.",
                "- Desenvolva cada seção com clareza. Não seja telegráfico nem prolixo.",
                f"- Contexto: {provided_params}/8 parâmetros. Cultura: {crop if crop and crop != 'geral' else 'geral'}."
            ])

            prompt = "\n".join(prompt_lines)

            response = self.model.generate_content(
                prompt,
                generation_config=self.config_analysis
            )
            response_text = response.text

            # Log da chamada
            log_data = self._log_api_call(prompt, response_text)

            return {
                "success": True,
                "recommendation": response_text,
                "parameters_provided": provided_params,
                "parameters_total": 8,
                "timestamp": datetime.now().isoformat(),
                "call_number": self.call_count,
                "mode": "complete_analysis",
                "crop": crop if crop and crop != 'geral' else None,
                "cost_this_call_usd": log_data['cost_this_call_usd'],
                "total_cost_usd": log_data['total_cost_usd']
            }

        except Exception as e:
            print(f"❌ Erro na análise completa: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._generate_fallback_analysis(soil_params),
                "timestamp": datetime.now().isoformat(),
                "parameters_provided": 0,
                "parameters_total": 8
            }

    def _generate_fallback_analysis(self, soil_params: Dict) -> str:
        """Gera análise básica quando a API falha"""
        ph = soil_params.get('ph', 0)
        humidity = soil_params.get('humidity', 0)

        analysis = f"ANÁLISE BÁSICA (modo offline):\n"
        analysis += f"• pH: {ph} - "
        if ph < 5.5:
            analysis += "ÁCIDO (corrigir com calcário)\n"
        elif ph > 7.5:
            analysis += "ALCALINO (corrigir com enxofre)\n"
        else:
            analysis += "IDEAL\n"

        analysis += f"• Umidade: {humidity}% - "
        if humidity < 30:
            analysis += "BAIXA (irrigação necessária)\n"
        elif humidity > 70:
            analysis += "ALTA (drenagem pode ser necessária)\n"
        else:
            analysis += "ADEQUADA\n"

        analysis += "\n⚠️ Serviço de IA temporariamente indisponível. Consulte um técnico agrícola."
        return analysis

    # ===================== ANÁLISE RÁPIDA (backward compatibility) =====================
    def analyze_soil(self, ph: float, humidity: float, nutrients: Dict = None):
        """Análise rápida para compatibilidade com versões anteriores"""
        if nutrients is None:
            nutrients = {}

        try:
            # Constrói dados para análise completa
            soil_params = {
                "ph": ph,
                "humidity": humidity,
                "nitrogen": nutrients.get('nitrogen'),
                "phosphorus": nutrients.get('phosphorus'),
                "potassium": nutrients.get('potassium'),
                "calcium": nutrients.get('calcium'),
                "magnesium": nutrients.get('magnesium'),
                "organic_matter": nutrients.get('organic_matter')
            }

            # Usa a análise completa
            result = self.analyze_soil_complete(soil_params)
            result["mode"] = "quick_analysis"
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": f"Análise básica: pH {ph}, Umidade {humidity}%.",
                "timestamp": datetime.now().isoformat()
            }

    # ===================== MODO CONVERSACIONAL =====================
    def start_conversation(self, session_id: str, initial_context: str = ""):
        """Inicia uma nova sessão conversacional"""
        if session_id in self.sessions:
            return {
                "success": True,
                "message": "Sessão retomada",
                "history": self.sessions[session_id]
            }

        # Inicia nova sessão
        self.sessions[session_id] = []

        greeting = """Você é um consultor agronômico sênior da EMBRAPA, especialista em fertilidade do solo.

COMO RESPONDER:
- Explique de forma clara e completa. Desenvolva o raciocínio técnico.
- Use dados concretos: dosagens (kg/ha, t/ha), prazos, épocas, produtos.
- Organize em tópicos quando houver mais de uma recomendação.
- Adapte a linguagem: técnica mas acessível ao produtor rural.
- Não repita o que o usuário já informou. Vá direto à orientação.

Estou pronto para ajudar. Qual sua dúvida?"""

        if initial_context:
            greeting = f"{greeting}\n\nNoto que você já tem dados do solo: {initial_context}.\nPosso explicar qualquer aspecto da análise ou responder perguntas específicas."

        # Log da sessão
        print(f"💬 Nova sessão iniciada: {session_id}")
        if initial_context:
            print(f"   Contexto inicial: {initial_context}")

        return {
            "success": True,
            "message": greeting,
            "session_id": session_id,
            "is_new": True,
            "timestamp": datetime.now().isoformat()
        }

    def _classify_message(self, text: str) -> str:
        """Classifica o tipo de mensagem do usuário para guiar o tom da resposta."""
        t = text.lower().strip()

        # Despedidas / encerramentos
        despedidas = ["tchau", "até mais", "ate mais", "até logo", "ate logo",
                      "adeus", "encerrar", "finalizar", "foi ótimo", "foi otimo",
                      "até a próxima", "ate a proxima", "boa noite", "boa tarde",
                      "bom dia", "até amanhã", "ate amanha", "flw", "vlw", "valeu"]
        # Agradecimentos simples (sem pergunta embutida)
        agradecimentos = ["obrigado", "obrigada", "obg", "grato", "grata",
                          "agradeço", "agradeco", "muito obrigado", "muito obrigada",
                          "thanks", "thank you", "ótimo", "otimo", "excelente",
                          "perfeito", "entendido", "compreendido", "ok, entendi",
                          "certo, entendi", "ficou claro", "ficou ótimo"]
        # Saudações
        saudacoes = ["oi", "olá", "ola", "hey", "e aí", "e ai", "tudo bem",
                     "tudo certo", "como vai", "boa", "salve"]

        for palavra in despedidas:
            if palavra in t and len(t) < 60:
                return "despedida"
        for palavra in agradecimentos:
            if t.startswith(palavra) or t == palavra:
                # Só é "puro" se não tiver pergunta embutida
                if "?" not in t and len(t) < 80:
                    return "agradecimento"
        for palavra in saudacoes:
            if t == palavra or t.startswith(palavra + " ") or t.startswith(palavra + ","):
                return "saudacao"
        return "tecnica"

    def send_message(self, session_id: str, user_message: str):
        """Processa uma mensagem em sessão existente"""
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Sessão não encontrada. Reinicie a conversa."
            }

        # Obtém histórico da sessão
        history = self.sessions[session_id]

        # Classifica o tipo de mensagem para adaptar o tom
        msg_type = self._classify_message(user_message)

        # Respostas locais para mensagens não técnicas (sem chamar API)
        import random
        if msg_type == "agradecimento":
            respostas = [
                "De nada! 😊 Fico feliz em ajudar. Se surgir mais alguma dúvida sobre o solo ou a lavoura, é só chamar!",
                "Por nada! Qualquer outra dúvida agrônoma, estou à disposição. Boas colheitas! 🌾",
                "Disponha! Se precisar de mais orientações sobre manejo ou fertilidade, estarei aqui.",
                "Fico feliz que tenha ajudado! Se tiver mais alguma pergunta sobre sua lavoura, pode perguntar. 🌱"
            ]
            resp = random.choice(respostas)
            self.sessions[session_id].append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})
            self.sessions[session_id].append({"role": "assistant", "content": resp, "timestamp": datetime.now().isoformat()})
            return {
                "success": True,
                "response": resp,
                "session_id": session_id,
                "history_length": len(self.sessions[session_id]),
                "timestamp": datetime.now().isoformat()
            }

        if msg_type == "despedida":
            respostas = [
                "Até logo! 👋 Boas colheitas e qualquer dúvida estou por aqui.",
                "Tchau! Foi um prazer ajudar. Sucesso na lavoura! 🌾",
                "Até mais! Se precisar de orientações agronômicas no futuro, estarei aqui. Boas colheitas! 🌱",
                "Boa sorte na sua produção! 👋 Até a próxima."
            ]
            resp = random.choice(respostas)
            self.sessions[session_id].append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})
            self.sessions[session_id].append({"role": "assistant", "content": resp, "timestamp": datetime.now().isoformat()})
            return {
                "success": True,
                "response": resp,
                "session_id": session_id,
                "history_length": len(self.sessions[session_id]),
                "timestamp": datetime.now().isoformat()
            }

        if msg_type == "saudacao":
            respostas = [
                "Olá! 👋 Sou seu consultor agronômico. Como posso ajudar sua lavoura hoje?",
                "Olá! 🌱 Pode perguntar — estou aqui para ajudar com solos, culturas e manejo.",
                "Oi! Tudo certo. Como posso ajudar com sua produção hoje? 🌾"
            ]
            resp = random.choice(respostas)
            self.sessions[session_id].append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})
            self.sessions[session_id].append({"role": "assistant", "content": resp, "timestamp": datetime.now().isoformat()})
            return {
                "success": True,
                "response": resp,
                "session_id": session_id,
                "history_length": len(self.sessions[session_id]),
                "timestamp": datetime.now().isoformat()
            }

        # ── Mensagem técnica: chama a API com prompt adequado ──
        prompt_lines = [
            "Você é um consultor agronômico sênior da EMBRAPA.",
            "Responda de forma COMPLETA, CLARA e BEM DESENVOLVIDA.",
            "Use dados concretos quando pertinente: dosagens (kg/ha, t/ha), prazos, épocas, produtos.",
            "Organize em tópicos quando houver múltiplas recomendações.",
            "Linguagem técnica mas acessível ao produtor rural.",
            "IMPORTANTE: responda APENAS o que foi perguntado. Não acrescente temas não solicitados.",
            "",
            "HISTÓRICO DA CONVERSA:"
        ]

        # Adiciona histórico (últimas 4 interações = 8 mensagens)
        for msg in history[-8:]:
            role = "USUÁRIO" if msg["role"] == "user" else "ASSISTENTE AGRONÔMICO"
            prompt_lines.append(f"{role}: {msg['content']}")

        prompt_lines.extend([
            f"\nPERGUNTA DO PRODUTOR: {user_message}",
            "",
            "Responda de forma objetiva e técnica. Inclua dosagens e justificativas quando a pergunta pedir.",
            "Não repita o que o usuário disse. Não adicione assuntos fora do escopo da pergunta."
        ])

        prompt = "\n".join(prompt_lines)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.config_conversation
            )
            response_text = response.text

            self._log_api_call(prompt, response_text)

            # Atualiza histórico
            self.sessions[session_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })

            self.sessions[session_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })

            print(f"💭 Mensagem processada na sessão {session_id}")

            return {
                "success": True,
                "response": response_text,
                "session_id": session_id,
                "history_length": len(self.sessions[session_id]),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Erro no chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": f"Desculpe, estou com dificuldades técnicas. Pergunta: '{user_message[:50]}...'"
            }

    def end_conversation(self, session_id: str):
        """Encerra uma sessão e salva o histórico"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Sessão não encontrada"}

        # Salva histórico antes de deletar
        try:
            os.makedirs('logs/conversations', exist_ok=True)
            history_file = f"logs/conversations/session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session_id,
                    "start_time": datetime.now().isoformat(),
                    "message_count": len(self.sessions[session_id]),
                    "history": self.sessions[session_id]
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Erro ao salvar histórico: {e}")

        # Remove sessão da memória
        del self.sessions[session_id]
        print(f"💤 Sessão encerrada: {session_id}")

        return {
            "success": True,
            "message": "Sessão encerrada e histórico salvo",
            "session_id": session_id
        }

    def get_session_stats(self, session_id: str):
        """Estatísticas da sessão"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Sessão não encontrada"}

        session_data = self.sessions[session_id]
        # LINHA CORRIGIDA:
        user_messages = [m for m in session_data if m["role"] == "user"]
        # Agora está fechado com o colchete correto.
        assistant_messages = [
            m for m in session_data if m["role"] == "assistant"]

        return {
            "success": True,
            "session_id": session_id,
            "total_messages": len(session_data),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "first_interaction": session_data[0]["timestamp"] if session_data else None,
            "last_interaction": session_data[-1]["timestamp"] if session_data else None
        }

    # ===================== ESTATÍSTICAS GERAIS =====================
    def get_service_stats(self):
        """Retorna estatísticas gerais do serviço"""
        total_sessions = len(self.sessions)
        active_sessions = sum(
            1 for session in self.sessions.values() if len(session) > 0)

        return {
            "service": "VitaGreen",
            "version": "3.0",
            "model": self.model_name,
            "total_api_calls": self.call_count,
            "total_cost_usd": round(self.total_estimated_cost, 6),
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "features": [
                "8-parameter-soil-analysis",
                "conversational-ai",
                "cost-tracking",
                "session-management"
            ],
            "supported_parameters": [
                "pH", "Humidity", "Nitrogen (N)", "Phosphorus (P)",
                "Potassium (K)", "Calcium (Ca)", "Magnesium (Mg)",
                "Organic Matter (MO)", "Crop-specific"
            ]
        }


# Instância global do serviço
gemini_service = GeminiAgricultureService()
