# main.py - Backend para análise completa de solo com IA LOCAL (Ollama)
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from uuid import uuid4
from datetime import datetime, timedelta
import uvicorn
import os
import json

# MUDANÇA: Ollama ao invés de Gemini - 100% gratuito e local!
from ollama_service import ollama_service
from database import db  # Banco de dados SQLite para salvar leituras
from conversion import (
    convert_npk_sensor_to_kg_ha,
    CONVERSION_FACTOR,
    SENSOR_MAX_MG_KG,
    SOIL_TYPES,
    get_density_by_soil_type,
    get_conversion_factor,
)

# NOVO: Sistema de autenticação profissional
from auth import get_current_user, get_current_user_optional, require_premium, jwt_manager
from user_database import user_db
from models import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    RefreshTokenRequest, ChangePasswordRequest, UpdateProfileRequest
)

# Mercado local (produtor / comprador / transportador)
from market_routes import router as market_router
from market_database import market_db as mkt_db

# ===================== MODELOS DE DADOS =====================
class SoilData(BaseModel):
    """Para análise completa com 8 parâmetros essenciais"""
    # 1-2. PARÂMETROS BÁSICOS (obrigatórios)
    ph: float
    humidity: float
    
    # 3-5. MACRONUTRIENTES PRIMÁRIOS (NPK - sensor em mg/kg, 0-2000)
    nitrogen: Optional[float] = None      # N (mg/kg → convertido para kg/ha)
    phosphorus: Optional[float] = None    # P (mg/kg → convertido para kg/ha)
    potassium: Optional[float] = None     # K (mg/kg → convertido para kg/ha)
    
    # 6-7. MACRONUTRIENTES SECUNDÁRIOS (opcionais)
    calcium: Optional[float] = None       # Ca (cmolc/dm³)
    magnesium: Optional[float] = None     # Mg (cmolc/dm³)
    
    # 8. MATÉRIA ORGÂNICA (opcional)
    organic_matter: Optional[float] = None  # MO (g/dm³)
    
    # Campo para compatibilidade com versão anterior
    nutrients: Optional[Dict[str, float]] = None
    
    # Cultura (para recomendações específicas)
    crop: Optional[str] = None

class ConversationMessage(BaseModel):
    """Para mensagens no chat"""
    session_id: str
    message: str
    soil_context: Optional[dict] = None

class ConversationStart(BaseModel):
    """Para iniciar conversa"""
    session_id: Optional[str] = None
    ph: Optional[float] = None
    humidity: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    organic_matter: Optional[float] = None
    crop: Optional[str] = None
    soil_type: Optional[str] = None
    region: Optional[str] = None

# ===================== NOVOS MODELOS PARA MEDIÇÃO =====================
class SensorReading(BaseModel):
    """Leitura individual do sensor"""
    sample_id: int
    ph: float
    humidity: float
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    organic_matter: Optional[float] = None
    timestamp: str = datetime.now().isoformat()

class SamplingSession(BaseModel):
    """Sessão de amostragem completa"""
    session_id: str
    total_samples: int
    readings: List[SensorReading] = []
    status: str = "active"  # active, completed, cancelled
    created_at: str = datetime.now().isoformat()

class StartSamplingRequest(BaseModel):
    """Request para iniciar amostragem"""
    total_samples: int = 20

# ===================== CONFIGURAÇÃO APP =====================
app = FastAPI(
    title="VitaGreen - Análise de Solo com Autenticação",
    description="Sistema profissional com IA Local, Autenticação JWT e Banco de Dados",
    version="4.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mercado local
app.include_router(market_router)

# Armazena sessões de amostragem ativas em memória
sampling_sessions: Dict[str, SamplingSession] = {}

# ===================== ENDPOINTS DE AUTENTICAÇÃO =====================

@app.post("/api/auth/register", response_model=TokenResponse, tags=["Autenticação"])
async def register_user(user_data: UserRegister):
    """
    Registra novo usuário no sistema
    
    - **email**: Email único do usuário
    - **password**: Senha (mínimo 6 caracteres) - será armazenada com hash bcrypt
    - **name**: Nome completo
    - **phone**: Telefone (opcional)
    - **farm_name**: Nome da fazenda/propriedade (opcional)
    """
    # Criar usuário
    result = user_db.create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        phone=user_data.phone,
        farm_name=user_data.farm_name,
        user_type=user_data.user_type or "produtor",
        cnpj=user_data.cnpj,
        company_name=user_data.company_name,
        city=user_data.city,
        state=user_data.state,
        vehicle_type=getattr(user_data, 'vehicle_type', None),
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Erro ao criar usuário")
        )

    # Criar perfil de mercado automaticamente
    mkt_db.upsert_profile(
        user_id=result["user_id"],
        user_type=user_data.user_type or "produtor",
        cnpj=user_data.cnpj,
        company_name=user_data.company_name,
        city=user_data.city,
        state=user_data.state,
    )
    
    # Criar tokens JWT
    token_data = {
        "sub": user_data.email,
        "user_id": result["user_id"],
        "name": user_data.name,
        "plan": "free"
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token(token_data)
    
    # Salvar refresh token no banco
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    user_db.save_refresh_token(result["user_id"], refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            user_id=result["user_id"],
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            farm_name=user_data.farm_name,
            plan="free",
            user_type=user_data.user_type or "produtor",
        )
    )


@app.post("/api/auth/login", response_model=TokenResponse, tags=["Autenticação"])
async def login_user(credentials: UserLogin):
    """
    Login de usuário existente
    
    - **email**: Email cadastrado
    - **password**: Senha
    
    Retorna tokens JWT para autenticação
    """
    # Autenticar usuário
    user = user_db.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )
    
    # Criar tokens JWT
    token_data = {
        "sub": user["email"],
        "user_id": user["user_id"],
        "name": user["name"],
        "plan": user["plan"]
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token(token_data)
    
    # Salvar refresh token no banco
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    user_db.save_refresh_token(user["user_id"], refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(**user)
    )


@app.post("/api/auth/refresh", response_model=TokenResponse, tags=["Autenticação"])
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """
    Renova access token usando refresh token
    
    Use quando o access token expirar (24h)
    """
    # Verificar refresh token no banco
    user_id = user_db.verify_refresh_token(refresh_data.refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido ou expirado"
        )
    
    # Buscar dados do usuário
    user = user_db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Criar novos tokens
    token_data = {
        "sub": user["email"],
        "user_id": user["id"],
        "name": user["name"],
        "plan": user["plan"]
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    new_refresh_token = jwt_manager.create_refresh_token(token_data)
    
    # Salvar novo refresh token
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    user_db.save_refresh_token(user["id"], new_refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse(**user)
    )


@app.get("/api/auth/me", response_model=UserResponse, tags=["Autenticação"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações do usuário logado
    
    Requer: Token JWT no header Authorization: Bearer <token>
    """
    user = user_db.get_user_by_id(current_user["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return UserResponse(**user)


@app.put("/api/auth/change-password", tags=["Autenticação"])
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Altera senha do usuário logado
    
    Requer autenticação
    """
    # Verificar senha antiga
    user = user_db.authenticate_user(current_user["email"], password_data.old_password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Senha atual incorreta")
    
    # Alterar senha
    user_db.change_password(current_user["user_id"], password_data.new_password)
    
    return {"success": True, "message": "Senha alterada com sucesso"}


@app.get("/api/auth/history", tags=["Autenticação"])
async def get_user_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna histórico de análises do usuário
    
    Requer autenticação
    """
    analyses = user_db.get_user_analyses(current_user["user_id"], limit)
    
    return {
        "success": True,
        "total": len(analyses),
        "analyses": analyses
    }

# ===================== ENDPOINTS PÚBLICOS =====================
@app.get("/")
async def redirect_to_login():
    """Redireciona para tela de login"""
    return FileResponse('static/login.html')

@app.get("/app")
async def serve_app():
    """Interface principal do app (requer login)"""
    return FileResponse('static/index.html')

@app.get("/mercado")
async def serve_mercado():
    """Página do mercado local"""
    return FileResponse('static/mercado.html')

@app.get("/perfil")
async def serve_perfil():
    """Página de perfil do usuário"""
    return FileResponse('static/perfil.html')

@app.get("/theme.js")
async def serve_theme_js():
    return FileResponse('static/theme.js', media_type='application/javascript')

@app.get("/auth.js")
async def serve_auth_js():
    return FileResponse('static/auth.js', media_type='application/javascript')

@app.get("/api/conversion")
async def get_conversion_info():
    """Retorna parâmetros da conversão e tabela de tipos de solo"""
    return {
        "factor_default": CONVERSION_FACTOR,
        "sensor_max_mg_kg": SENSOR_MAX_MG_KG,
        "formula": "kg/ha = mg/kg × (área × profundidade × densidade) / 1.000.000",
        "soil_types": SOIL_TYPES,
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VitaGreen - IA Local",
        "features": ["analise-simples", "chat-amigavel", "sensor-integration", "database-storage"]
    }

# ----- ANÁLISE COMPLETA (SIMPLIFICADA PARA AGRICULTORES) -----
@app.post("/api/analyze", tags=["Análise de Solo"])
async def analyze_soil(
    data: SoilData,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Análise simples e direta do solo
    
    - Pode ser usada SEM login (acesso público)
    - Se logado, salva no histórico do usuário
    """
    try:
        # Constrói dicionário com os dados
        soil_params = {
            "ph": data.ph,
            "humidity": data.humidity,
            "nitrogen": data.nitrogen,
            "phosphorus": data.phosphorus,
            "potassium": data.potassium,
            "crop": data.crop,
        }
        
        # Remove valores None
        clean_params = {k: v for k, v in soil_params.items() if v is not None}
        
        # Chama IA local (Ollama) - análise simples e prática
        analysis = ollama_service.analyze_soil_simple(clean_params)
        
        # Se usuário estiver logado, salvar no histórico
        if current_user:
            user_db.save_user_analysis(
                user_id=current_user["user_id"],
                session_id=str(uuid4())[:8],
                analysis_type="soil_analysis",
                input_data=json.dumps(clean_params),
                result=analysis
            )
        
        return {
            "success": True,
            "analysis": analysis,
            "data": clean_params,
            "model": "Ollama Local - 100% Gratuito",
            "saved_to_history": current_user is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar a análise. Tente novamente.")

# ----- CONVERSACIONAL (CHAT SIMPLES E AMIGÁVEL) -----
@app.post("/api/conversation/start")
async def start_conversation(data: ConversationStart):
    """Inicia nova conversa com contexto completo do solo"""
    try:
        session_id = data.session_id or f"chat_{str(uuid4())[:8]}"

        # Monta contexto completo do solo
        soil_data = None
        if data.ph and data.humidity:
            soil_data = {
                "ph": data.ph,
                "humidity": data.humidity,
                "nitrogen": data.nitrogen,
                "phosphorus": data.phosphorus,
                "potassium": data.potassium,
                "calcium": data.calcium,
                "magnesium": data.magnesium,
                "organic_matter": data.organic_matter,
                "crop": data.crop,
                "soil_type": data.soil_type,
                "region": data.region,
            }

        greeting = ollama_service.start_conversation(session_id, soil_data)

        return {
            "success": True,
            "session_id": session_id,
            "message": greeting
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao iniciar conversa. Tente novamente.")

@app.post("/api/conversation/message")
async def send_message(data: ConversationMessage):
    """Envia mensagem no chat"""
    try:
        response = ollama_service.chat_conversation(
            data.session_id,
            data.message,
            soil_context=data.soil_context
        )
        return {
            "success": True,
            "message": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar mensagem. Tente novamente.")

# ----- INTEGRAÇÃO COM SENSOR (SALVA NO BANCO AUTOMATICAMENTE) -----
@app.post("/api/sensor/reading")
async def save_sensor_reading(reading: SensorReading):
    """Recebe e salva leitura do sensor no banco de dados"""
    try:
        # Salvar no banco de dados
        reading_id = db.save_sensor_reading({
            'session_id': reading.session_id,
            'sample_number': reading.sample_id,
            'ph': reading.ph,
            'humidity': reading.humidity,
            'nitrogen': reading.nitrogen,
            'phosphorus': reading.phosphorus,
            'potassium': reading.potassium,
            'timestamp': reading.timestamp,
            'notes': None
        })
        
        return {
            "success": True,
            "reading_id": reading_id,
            "message": f"Leitura {reading.sample_id} salva no banco de dados",
            "session_id": reading.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensor/session/{session_id}")
async def get_session_data(session_id: str):
    """Busca todas as leituras de uma sessão"""
    try:
        readings = db.get_session_readings(session_id)
        average = db.calculate_session_average(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "total_readings": len(readings),
            "readings": readings,
            "average": average
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sensor/analyze_session/{session_id}")
async def analyze_sensor_session(session_id: str):
    """Analisa a média de todas as leituras de uma sessão"""
    try:
        average = db.calculate_session_average(session_id)
        
        if not average or average['total_readings'] == 0:
            raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para esta sessão")
        
        # Analisar com IA local
        analysis = ollama_service.analyze_soil_simple(average)
        
        return {
            "success": True,
            "session_id": session_id,
            "total_readings": average['total_readings'],
            "average_values": average,
            "analysis": analysis,
            "model": "Ollama Local - 100% Gratuito"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----- MODO DE AMOSTRAGEM (NOVO) -----
@app.post("/api/sampling/start")
async def start_sampling_session(request: StartSamplingRequest):
    """Inicia nova sessão de amostragem"""
    try:
        session_id = f"sample_{str(uuid4())[:8]}"
        total_samples = request.total_samples
        
        # Validação: máximo de 100 amostras
        if total_samples > 100:
            raise HTTPException(status_code=400, detail="Número máximo de amostras é 100")
        
        session = SamplingSession(
            session_id=session_id,
            total_samples=total_samples,
            status="active",
            created_at=datetime.now().isoformat()
        )
        
        sampling_sessions[session_id] = session
        
        return {
            "success": True,
            "session_id": session_id,
            "total_samples": total_samples,
            "message": f"Sessão de amostragem iniciada para {total_samples} pontos"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sampling/add_reading")
async def add_sensor_reading(session_id: str, reading: SensorReading):
    """Adiciona uma leitura do sensor à sessão"""
    try:
        if session_id not in sampling_sessions:
            raise HTTPException(status_code=404, detail="Sessão de amostragem não encontrada")
        
        session = sampling_sessions[session_id]
        
        # Verifica se a sessão ainda está ativa
        if session.status != "active":
            raise HTTPException(status_code=400, detail=f"Sessão está {session.status}")
        
        # Verifica se não excedeu o número máximo de amostras
        if len(session.readings) >= session.total_samples:
            session.status = "completed"
            return {
                "success": False,
                "error": "Número máximo de amostras atingido",
                "session_id": session_id,
                "current_count": len(session.readings),
                "total_samples": session.total_samples,
                "is_complete": True
            }
        
        # Adiciona timestamp atual se não fornecido
        if not reading.timestamp:
            reading.timestamp = datetime.now().isoformat()
        
        # Adiciona leitura à sessão
        session.readings.append(reading)
        
        # Verifica se completou
        is_complete = len(session.readings) == session.total_samples
        if is_complete:
            session.status = "completed"
        
        return {
            "success": True,
            "session_id": session_id,
            "current_count": len(session.readings),
            "total_samples": session.total_samples,
            "is_complete": is_complete,
            "sample_id": reading.sample_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sampling/calculate_averages/{session_id}")
async def calculate_averages(session_id: str):
    """Calcula médias de todas as leituras da sessão"""
    try:
        if session_id not in sampling_sessions:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        session = sampling_sessions[session_id]
        
        if len(session.readings) == 0:
            raise HTTPException(status_code=400, detail="Nenhuma leitura registrada")
        
        # Coleta todos os valores por parâmetro
        all_ph = [r.ph for r in session.readings]
        all_humidity = [r.humidity for r in session.readings]
        all_nitrogen = [r.nitrogen for r in session.readings if r.nitrogen is not None]
        all_phosphorus = [r.phosphorus for r in session.readings if r.phosphorus is not None]
        all_potassium = [r.potassium for r in session.readings if r.potassium is not None]
        all_calcium = [r.calcium for r in session.readings if r.calcium is not None]
        all_magnesium = [r.magnesium for r in session.readings if r.magnesium is not None]
        all_organic_matter = [r.organic_matter for r in session.readings if r.organic_matter is not None]
        
        # Função auxiliar para calcular média e desvio padrão
        def calculate_stats(values, param_name=""):
            if not values:
                return None
            
            avg = sum(values) / len(values)
            
            # Desvio padrão simples
            if len(values) > 1:
                variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
                std_dev = variance ** 0.5
            else:
                std_dev = 0.0
            
            # Coeficiente de variação (CV%)
            cv_percent = (std_dev / avg * 100) if avg != 0 else 0
            
            return {
                "average": round(avg, 2),
                "std_dev": round(std_dev, 2),
                "cv_percent": round(cv_percent, 1),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "count": len(values),
                "unit": get_param_unit(param_name)
            }
        
        # Função auxiliar para obter unidade
        def get_param_unit(param):
            units = {
                "ph": "",
                "humidity": "%",
                "nitrogen": "mg/dm³",
                "phosphorus": "mg/dm³",
                "potassium": "mmolc/dm³",
                "calcium": "cmolc/dm³",
                "magnesium": "cmolc/dm³",
                "organic_matter": "g/dm³"
            }
            return units.get(param, "")
        
        averages = {
            "ph": calculate_stats(all_ph, "ph"),
            "humidity": calculate_stats(all_humidity, "humidity"),
            "nitrogen": calculate_stats(all_nitrogen, "nitrogen"),
            "phosphorus": calculate_stats(all_phosphorus, "phosphorus"),
            "potassium": calculate_stats(all_potassium, "potassium"),
            "calcium": calculate_stats(all_calcium, "calcium"),
            "magnesium": calculate_stats(all_magnesium, "magnesium"),
            "organic_matter": calculate_stats(all_organic_matter, "organic_matter")
        }
        
        # Calcula média geral de qualidade (baseada no CV)
        valid_cvs = [avg["cv_percent"] for avg in averages.values() if avg is not None]
        if valid_cvs:
            avg_cv = sum(valid_cvs) / len(valid_cvs)
            if avg_cv < 10:
                quality = "excelente"
            elif avg_cv < 20:
                quality = "boa"
            elif avg_cv < 30:
                quality = "regular"
            else:
                quality = "alta_variabilidade"
        else:
            quality = "indeterminada"
        
        return {
            "success": True,
            "session_id": session_id,
            "total_readings": len(session.readings),
            "expected_readings": session.total_samples,
            "completion_percent": round((len(session.readings) / session.total_samples) * 100, 1),
            "averages": averages,
            "data_quality": quality,
            "readings_summary": [
                {
                    "sample_id": r.sample_id,
                    "ph": r.ph,
                    "humidity": r.humidity,
                    "timestamp": r.timestamp
                } for r in session.readings[:10]  # Retorna apenas as primeiras 10 para resumo
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sampling/session/{session_id}")
async def get_sampling_session(session_id: str):
    """Obtém informações de uma sessão de amostragem"""
    try:
        if session_id not in sampling_sessions:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        session = sampling_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "total_samples": session.total_samples,
            "current_samples": len(session.readings),
            "status": session.status,
            "created_at": session.created_at,
            "progress": f"{len(session.readings)}/{session.total_samples}",
            "progress_percent": round((len(session.readings) / session.total_samples) * 100, 1) if session.total_samples > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sampling/end/{session_id}")
async def end_sampling_session(session_id: str):
    """Encerra uma sessão de amostragem"""
    try:
        if session_id in sampling_sessions:
            session = sampling_sessions[session_id]
            session.status = "cancelled"
            del sampling_sessions[session_id]
            
            return {
                "success": True,
                "message": "Sessão de amostragem encerrada",
                "session_id": session_id,
                "total_readings_collected": len(session.readings)
            }
        
        return {"success": False, "error": "Sessão não encontrada"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sampling/active_sessions")
async def get_active_sampling_sessions():
    """Lista todas as sessões de amostragem ativas"""
    try:
        active_sessions = [
            {
                "session_id": session_id,
                "total_samples": session.total_samples,
                "current_samples": len(session.readings),
                "status": session.status,
                "created_at": session.created_at,
                "progress_percent": round((len(session.readings) / session.total_samples) * 100, 1) if session.total_samples > 0 else 0
            }
            for session_id, session in sampling_sessions.items()
            if session.status == "active"
        ]
        
        return {
            "success": True,
            "active_sessions": active_sessions,
            "total_active": len(active_sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----- ESTATÍSTICAS GERAIS -----
@app.get("/api/stats")
async def get_stats():
    """Estatísticas gerais do serviço"""
    try:
        total_sampling_readings = sum(len(session.readings) for session in sampling_sessions.values())
        
        return {
            "success": True,
            "service": "VitaGreen - IA Local",
            "version": "4.0",
            "total_calls": ollama_service.call_count,
            "total_sessions": len(ollama_service.sessions),
            "total_cost_usd": 0.0,  # 100% gratuito com Ollama!
            "active_model": ollama_service.model_name,
            "ai_type": "Ollama Local - Sem custos!",
            "sampling_stats": {
                "active_sampling_sessions": len([s for s in sampling_sessions.values() if s.status == "active"]),
                "total_sampling_sessions": len(sampling_sessions),
                "total_sampling_readings": total_sampling_readings
            },
            "features": [
                "analise-simples-e-pratica",
                "chat-amigavel",
                "integracao-sensor",
                "banco-de-dados",
                "100%-gratuito"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== INICIALIZAÇÃO =====================
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    
    print("\n" + "="*65)
    print("🚀 VITAGREEN - ANÁLISE DE SOLO COM MODO DE AMOSTRAGEM")
    print("="*65)
    print("📊 Parâmetros suportados:")
    print("   1. pH | 2. Umidade | 3. Nitrogênio (N) | 4. Fósforo (P)")
    print("   5. Potássio (K) | 6. Cálcio (Ca) | 7. Magnésio (Mg)")
    print("   8. Matéria Orgânica (MO)")
    print("\n🎯 NOVO: Modo de Amostragem Múltipla")
    print("   • 1-100 pontos de coleta")
    print("   • Cálculo automático de médias")
    print("   • Análise de variabilidade")
    print("\n📂 Diretório atual:", os.getcwd())
    print("🌐 Acesse: http://localhost:8000")
    print("⏹️  Pressione Ctrl+C para parar")
    print("="*65 + "\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)