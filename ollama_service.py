# ollama_service.py - Serviço de IA local usando Ollama
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# Informações de clima por estado brasileiro
REGION_CLIMATE = {
    "MT": "Mato Grosso — clima tropical com seca pronunciada (maio a setembro), chuvas concentradas no verão (outubro a abril), cerrado e transição para Amazônia. Solos predominantemente Latossolos, bem drenados.",
    "MS": "Mato Grosso do Sul — clima tropical com estação seca definida, verões quentes e úmidos, invernos secos. Cerrado e Pantanal. Latossolos e Neossolos.",
    "GO": "Goiás — clima tropical de cerrado, chuvas de outubro a março, seca de abril a setembro. Solos Latossolos Vermelho-Amarelo.",
    "DF": "Distrito Federal — clima tropical de altitude, seca intensa de maio a setembro. Latossolos.",
    "RS": "Rio Grande do Sul — clima subtropical úmido, geadas no inverno, chuvas bem distribuídas. Solos férteis: Latossolos e Nitossolos.",
    "SC": "Santa Catarina — clima subtropical, chuvas bem distribuídas, geadas no inverno. Solos variados, Cambissolos e Nitossolos.",
    "PR": "Paraná — clima subtropical a tropical, chuvas regulares, solos férteis Terra Roxa (Nitossolo Vermelho). Produção agrícola intensa.",
    "SP": "São Paulo — clima tropical de altitude no interior, subtropical no sul. Solos variados: Terra Roxa, Latossolos. Veranico possível.",
    "MG": "Minas Gerais — clima variado: tropical no norte, subtropical no sul, altitude no Triângulo. Chuvas concentradas no verão. Latossolos e Cambissolos.",
    "RJ": "Rio de Janeiro — clima tropical úmido, chuvas abundantes. Solos rasos em morros.",
    "ES": "Espírito Santo — clima tropical úmido, chuvas regulares. Solos Latossolos e Argissolos.",
    "BA": "Bahia — clima variado: semiárido no sertão (déficit hídrico severo), tropical úmido no litoral. Solos rasos no semiárido, Latossolos no oeste.",
    "PI": "Piauí — clima semiárido a tropical, chuvas concentradas (jan-abr), longa estiagem. MATOPIBA: solos de Cerrado no sul.",
    "MA": "Maranhão — transição Amazônia/Cerrado/Semiárido. Chuvas de jan-jun. MATOPIBA no sul.",
    "CE": "Ceará — clima semiárido, chuvas irregulares e escassas. Solos rasos e pedregosos. Irrigação essencial.",
    "PE": "Pernambuco — semiárido no sertão, tropical no litoral. Chuvas irregulares no interior.",
    "RN": "Rio Grande do Norte — semiárido, chuvas escassas e irregulares.",
    "PB": "Paraíba — semiárido predominante, chuvas de fev-jun no Agreste.",
    "SE": "Sergipe — tropical úmido no litoral, semiárido no interior.",
    "AL": "Alagoas — tropical úmido no litoral, déficit hídrico no sertão.",
    "PA": "Pará — clima equatorial úmido, chuvas intensas (jan-jun), temperatura alta. Latossolos Amarelos, alta acidez.",
    "AM": "Amazonas — equatorial, chuvas durante todo o ano, umidade muito alta. Solos ácidos e pobres em nutrientes.",
    "RO": "Rondônia — equatorial com estação seca (mai-set). Solos Latossolos, desmatamento recente com solos em recuperação.",
    "TO": "Tocantins — cerrado, chuvas out-abr, seca mai-set. MATOPIBA. Latossolos.",
    "AP": "Amapá — equatorial, chuvas intensas. Solos ácidos.",
    "RR": "Roraima — tropical com savana, chuvas mai-out. Solos variados.",
    "AC": "Acre — equatorial úmido. Solos argilosos, alta umidade.",
}

class OllamaAgricultureService:
    def __init__(self):
        print("🌱 Iniciando serviço Ollama IA Local...")
        self.base_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print(f"✅ Ollama conectado! Modelo: {self.model_name}")
            else:
                print("⚠️  Ollama não está respondendo corretamente")
        except Exception as e:
            print(f"❌ ERRO: Ollama não está rodando. Inicie com: ollama serve")
        
        self.sessions: Dict[str, List[Dict]] = {}
        self.call_count = 0
        print("   ✅ Serviço 100% gratuito e local!")

    def _sanitize_response(self, text: str) -> str:
        """Remove ou traduz palavras comuns em inglês que o modelo insiste em usar"""
        replacements = {
            "called ": "chamada ",
            "toxicity": "toxicidade",
            "deficiency": "deficiência",
            "soil": "solo",
            "crop": "cultura",
            "fertilizer": "adubo",
            "limestone": "calcário",
            "organic matter": "matéria orgânica",
            "pH level": "nível de pH",
            "nutrient": "nutriente",
            "compost": "composto orgânico",
            "harvest": "colheita",
            "yield": "produção",
            "rainfall": "chuva",
            "drainage": "drenagem",
            "acidity": "acidez",
            "alkaline": "alcalino",
            "micronutrient": "micronutriente",
            "macronutrient": "macronutriente",
            "root": "raiz",
            "growth": "crescimento",
            "amendment": "correção",
            "application": "aplicação",
            "management": "manejo",
            "recommendation": "recomendação",
            "analysis": "análise",
        }
        result = text
        for en, pt in replacements.items():
            result = result.replace(en, pt)
        return result

    def _call_ollama(self, prompt: str, system_prompt: str = "", max_tokens: int = 600) -> str:
        """Chama o Ollama local"""
        self.call_count += 1
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": max_tokens,
                    "top_p": 0.85,
                    "repeat_penalty": 1.1,
                }
            }
            print(f"\n🤖 Chamada #{self.call_count} ao Ollama...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=90
            )
            if response.status_code == 200:
                result = response.json()
                raw = result.get("response", "").strip()
                return self._sanitize_response(raw)
            else:
                return f"Erro na comunicação com Ollama: {response.status_code}"
        except Exception as e:
            print(f"❌ Erro: {e}")
            return "Não consegui processar agora. Verifique se o Ollama está rodando."

    def _build_soil_summary(self, soil_data: Dict) -> str:
        """Monta resumo completo dos dados do solo"""
        lines = []
        lines.append(f"- pH: {soil_data.get('ph', 'não informado')}")
        lines.append(f"- Umidade: {soil_data.get('humidity', 'não informada')}%")
        
        if soil_data.get('nitrogen') is not None:
            lines.append(f"- Nitrogênio (N): {soil_data['nitrogen']} mg/kg")
        if soil_data.get('phosphorus') is not None:
            lines.append(f"- Fósforo (P): {soil_data['phosphorus']} mg/kg")
        if soil_data.get('potassium') is not None:
            lines.append(f"- Potássio (K): {soil_data['potassium']} mg/kg")
        if soil_data.get('calcium') is not None:
            lines.append(f"- Cálcio (Ca): {soil_data['calcium']} cmolc/dm³")
        if soil_data.get('magnesium') is not None:
            lines.append(f"- Magnésio (Mg): {soil_data['magnesium']} cmolc/dm³")
        if soil_data.get('organic_matter') is not None:
            lines.append(f"- Matéria Orgânica: {soil_data['organic_matter']} g/dm³")
        if soil_data.get('crop'):
            lines.append(f"- Cultura pretendida: {soil_data['crop']}")
        if soil_data.get('soil_type'):
            lines.append(f"- Tipo de solo: {soil_data['soil_type']}")

        region = soil_data.get('region')
        if region and region in REGION_CLIMATE:
            lines.append(f"- Região: {REGION_CLIMATE[region]}")
        elif region:
            lines.append(f"- Região: {region}")

        return "\n".join(lines)

    def analyze_soil_simple(self, soil_data: Dict) -> str:
        """Análise completa e prática para o agricultor"""

        region = soil_data.get('region', '')
        climate_info = REGION_CLIMATE.get(region, '') if region else ''
        crop = soil_data.get('crop', '')

        system_prompt = f"""Você é um agrônomo brasileiro que ajuda pequenos agricultores.
REGRA PRINCIPAL: Responda SOMENTE em português do Brasil. Nunca use palavras em inglês.
Use linguagem simples, como numa conversa. Evite termos técnicos. Quando usar um termo técnico, explique com palavras simples.
Seja direto e prático: diga o que o agricultor deve fazer, quanto usar e quando.
{"Região e clima: " + climate_info if climate_info else ""}
{"Cultura plantada: " + crop if crop else ""}"""

        soil_summary = self._build_soil_summary(soil_data)

        prompt = f"""Analise os dados do solo abaixo e responda em português do Brasil. NÃO use inglês em nenhuma palavra.

{soil_summary}

Responda com estas 4 partes, usando linguagem simples:

1. ✅ COMO ESTÁ O SOLO AGORA
Explique de forma simples o que está bom e o que está ruim.

2. 🔧 O QUE FAZER PRIMEIRO
Liste de 2 a 4 ações urgentes. Para cada uma diga: o que é, quanto usar e quando fazer.

3. 🌱 DICA PARA A CULTURA
O que precisa para ter uma boa colheita de {crop if crop else 'qualquer cultura'}.

4. 💡 DICA DE LONGO PRAZO
Uma ação simples para melhorar o solo nos próximos meses.

Escreva como se estivesse conversando com um agricultor. Responda somente em português."""

        return self._call_ollama(prompt, system_prompt, max_tokens=700)

    def _classify_message(self, text: str) -> str:
        """Detecta se a mensagem é social (agradecimento, despedida, saudação) ou técnica."""
        t = text.lower().strip()

        despedidas = [
            "tchau", "até mais", "ate mais", "até logo", "ate logo", "adeus",
            "boa noite", "boa tarde", "bom dia", "até amanhã", "ate amanha",
            "até a próxima", "ate a proxima", "flw", "vlw", "foi ótimo",
            "foi otimo", "encerrar", "finalizar", "obrigado até", "obrigada até"
        ]
        agradecimentos = [
            "obrigado", "obrigada", "obg", "grato", "grata", "valeu",
            "muito obrigado", "muito obrigada", "agradeço", "agradeco",
            "ótimo obrigado", "otimo obrigado", "perfeito obrigado",
            "entendido", "compreendido", "ficou claro", "ficou ótimo",
            "ficou otimo", "ok entendi", "certo entendi", "show",
            "excelente", "perfeito", "ótimo", "otimo", "maravilha",
            "tá bom", "ta bom", "tá ótimo", "ta otimo"
        ]
        saudacoes = [
            "oi", "olá", "ola", "ei", "hey", "e aí", "e ai",
            "tudo bem", "tudo bom", "tudo certo", "como vai", "boa", "salve"
        ]

        # Despedida (pode conter "obrigado" + "tchau" juntos)
        for p in despedidas:
            if p in t and len(t) < 70:
                return "despedida"

        # Agradecimento puro: começa com a palavra e não tem "?"
        for p in agradecimentos:
            if (t == p or t.startswith(p + " ") or t.startswith(p + "!") or t.startswith(p + ",")):
                if "?" not in t and len(t) < 80:
                    return "agradecimento"

        # Saudação pura (sem pergunta técnica)
        for p in saudacoes:
            if (t == p or t.startswith(p + " ") or t.startswith(p + "!") or t.startswith(p + ",")):
                if "?" not in t and len(t) < 50:
                    return "saudacao"

        return "tecnica"

    def chat_conversation(self, session_id: str, user_message: str, soil_context: Optional[Dict] = None) -> str:
        """Conversa natural e completa sobre agricultura"""
        import random

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # ── Resposta imediata para mensagens sociais (sem chamar o Ollama) ──
        msg_type = self._classify_message(user_message)

        if msg_type == "agradecimento":
            respostas = [
                "De nada! 😊 Qualquer dúvida sobre a lavoura, é só chamar.",
                "Por nada! Se precisar de mais orientações, estou aqui. Boas colheitas! 🌾",
                "Disponha! Boa sorte na sua plantação. 🌱",
                "Fico feliz em ajudar! Se surgir mais alguma dúvida, pode perguntar. 🌾"
            ]
            response = random.choice(respostas)
            self.sessions[session_id].append({"role": "Agricultor", "content": user_message})
            self.sessions[session_id].append({"role": "Agrônomo", "content": response})
            return response

        if msg_type == "despedida":
            respostas = [
                "Até logo! 👋 Boas colheitas e qualquer dúvida estou por aqui.",
                "Tchau! Foi um prazer ajudar. Sucesso na lavoura! 🌾",
                "Até mais! Se precisar de orientações agronômicas, estarei aqui. 🌱",
                "Boa sorte na sua produção! 👋 Até a próxima."
            ]
            response = random.choice(respostas)
            self.sessions[session_id].append({"role": "Agricultor", "content": user_message})
            self.sessions[session_id].append({"role": "Agrônomo", "content": response})
            return response

        if msg_type == "saudacao":
            respostas = [
                "Olá! 👋 Sou o Agro.IA. Como posso ajudar sua lavoura hoje?",
                "Oi! 🌱 Pode perguntar — estou aqui para ajudar com solos, culturas e manejo.",
                "Olá! Tudo bem? Como posso ajudar com sua produção hoje? 🌾"
            ]
            response = random.choice(respostas)
            self.sessions[session_id].append({"role": "Agricultor", "content": user_message})
            self.sessions[session_id].append({"role": "Agrônomo", "content": response})
            return response

        # ── Mensagem técnica: envia ao Ollama ──
        region = (soil_context or {}).get('region', '')
        climate_info = REGION_CLIMATE.get(region, '') if region else ''
        crop = (soil_context or {}).get('crop', '')

        system_prompt = f"""Você é um agrônomo brasileiro amigo do agricultor.
Responda SOMENTE em português. Seja breve e direto — máximo 3 frases por resposta.
Responda APENAS o que foi perguntado, sem adicionar assuntos extras.
{"Clima da região: " + climate_info if climate_info else ""}
{"Cultura plantada: " + crop if crop else ""}"""

        # Monta contexto do solo
        soil_info = ""
        if soil_context:
            soil_info = "\n[Dados do solo do agricultor]\n" + self._build_soil_summary(soil_context)

        # Histórico recente
        history = ""
        if self.sessions[session_id]:
            recent = self.sessions[session_id][-6:]
            for msg in recent:
                history += f"\n{msg['role']}: {msg['content']}"

        full_prompt = f"{soil_info}\n\nHistórico:\n{history}\n\nAgricultor: {user_message}\n\nAgrônomo (resposta curta, máximo 3 frases, somente português):"

        response = self._call_ollama(full_prompt, system_prompt, max_tokens=250)

        self.sessions[session_id].append({"role": "Agricultor", "content": user_message})
        self.sessions[session_id].append({"role": "Agrônomo", "content": response})

        return response

    def start_conversation(self, session_id: str, soil_data: Optional[Dict] = None) -> str:
        """Inicia conversa com contexto completo"""

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        region = (soil_data or {}).get('region', '')
        climate_info = REGION_CLIMATE.get(region, '') if region else ''
        crop = (soil_data or {}).get('crop', '')

        system_prompt = f"""Você é um agrônomo brasileiro amigável.
REGRA PRINCIPAL: Responda SOMENTE em português do Brasil. Nunca escreva palavras em inglês.
Use linguagem simples. Seja direto e amigável.
{"Região: " + climate_info if climate_info else ""}
{"Cultura: " + crop if crop else ""}"""

        if soil_data and soil_data.get('ph') and soil_data.get('humidity'):
            soil_summary = self._build_soil_summary(soil_data)
            prompt = f"""O agricultor recebeu a análise do solo:

{soil_summary}

Escreva somente em português do Brasil. Dê uma saudação curta e amigável (máximo 3 frases) e faça UMA pergunta simples sobre o que ele quer melhorar na plantação. Não use inglês."""
        else:
            prompt = "Escreva somente em português do Brasil. Cumprimente o agricultor de forma amigável e pergunte sobre a plantação dele. Máximo 2 frases. Não use inglês."

        response = self._call_ollama(prompt, system_prompt, max_tokens=200)
        self.sessions[session_id].append({"role": "Agrônomo", "content": response})
        return response


ollama_service = OllamaAgricultureService()
