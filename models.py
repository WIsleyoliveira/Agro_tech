# models.py - Modelos de dados para autenticação
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Modelo para registro de novo usuário"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Mínimo 6 caracteres")
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    farm_name: Optional[str] = None
    user_type: Optional[str] = "produtor"   # produtor | comprador | transportador
    cnpj: Optional[str] = None
    company_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    vehicle_type: Optional[str] = None      # para transportador

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        return v

    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in {"produtor", "comprador", "transportador"}:
            raise ValueError('Tipo deve ser: produtor, comprador ou transportador')
        return v


class UserLogin(BaseModel):
    """Modelo para login de usuário"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Resposta com dados do usuário (sem senha)"""
    user_id: int
    email: str
    name: str
    phone: Optional[str] = None
    farm_name: Optional[str] = None
    plan: str = "free"
    user_type: Optional[str] = "produtor"
    created_at: Optional[str] = None
    last_login: Optional[str] = None


class TokenResponse(BaseModel):
    """Resposta com tokens de autenticação"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 horas em segundos
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Request para renovar token"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Request para trocar senha"""
    old_password: str
    new_password: str = Field(..., min_length=6)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Nova senha deve ter no mínimo 6 caracteres')
        return v


class UpdateProfileRequest(BaseModel):
    """Request para atualizar perfil"""
    name: Optional[str] = None
    phone: Optional[str] = None
    farm_name: Optional[str] = None
