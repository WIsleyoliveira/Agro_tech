# auth.py - Sistema de autenticação JWT profissional
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

# Configurações de segurança
SECRET_KEY = secrets.token_urlsafe(32)  # Gera chave secreta aleatória
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 dias

# Security scheme para FastAPI
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)  # Não dá erro se token não existir


class PasswordHasher:
    """Gerenciador de hash de senhas"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash seguro da senha"""
        if len(password) > 72:
            raise ValueError("A senha deve ter no máximo 72 caracteres.")
        if len(password) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False


class JWTManager:
    """Gerenciador de tokens JWT"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token de acesso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Cria token de refresh JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica e decodifica o token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado. Faça login novamente."
            )
        except (jwt.PyJWTError, jwt.DecodeError, jwt.InvalidTokenError, Exception):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido. Acesso negado."
            )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency para proteger rotas - extrai usuário do token
    Uso: @app.get("/rota-protegida")
         async def rota(user = Depends(get_current_user)):
    """
    token = credentials.credentials
    payload = JWTManager.verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido"
        )
    
    user_email = payload.get("sub")
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    return {
        "email": user_email,
        "user_id": payload.get("user_id"),
        "name": payload.get("name"),
        "plan": payload.get("plan", "free")
    }


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[dict]:
    """
    Dependency opcional - retorna usuário se logado, None se não
    Uso para rotas que funcionam com ou sem login
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = JWTManager.verify_token(token)
        
        if payload.get("type") != "access":
            return None
        
        user_email = payload.get("sub")
        if user_email is None:
            return None
        
        return {
            "email": user_email,
            "user_id": payload.get("user_id"),
            "name": payload.get("name"),
            "plan": payload.get("plan", "free")
        }
    except:
        return None


def require_premium(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency para rotas premium (usuários com sensor)
    Uso: @app.get("/rota-premium")
         async def rota(user = Depends(require_premium)):
    """
    if user.get("plan") not in ["premium", "sensor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta funcionalidade requer um plano premium ou sensor conectado"
        )
    return user


# Instâncias globais
password_hasher = PasswordHasher()
jwt_manager = JWTManager()
