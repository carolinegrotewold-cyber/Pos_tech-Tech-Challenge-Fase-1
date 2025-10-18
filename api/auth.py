import os
from datetime import datetime, timedelta
from typing import Optional

import jwt  # PyJWT
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router_auth = APIRouter()

# -------- Configuração básica (poderia vir de variáveis de ambiente) --------
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ACCESS_EXPIRES_MIN = 30          # access token dura 30 minutos
REFRESH_EXPIRES_DAYS = 7         # refresh token dura 7 dias

# Credenciais de demonstração (troque por variáveis de ambiente em prod)
DEMO_USER = os.getenv("DEMO_USER", "admin")
DEMO_PASS = os.getenv("DEMO_PASS", "admin123")


# ----------------------------- Modelos Pydantic ------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


# ----------------------------- Utilitários JWT -------------------------------
def _create_token(username: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": username,                  # subject
        "type": token_type,               # "access" ou "refresh"
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_access_token(username: str) -> str:
    return _create_token(username, "access", timedelta(minutes=ACCESS_EXPIRES_MIN))

def create_refresh_token(username: str) -> str:
    return _create_token(username, "refresh", timedelta(days=REFRESH_EXPIRES_DAYS))

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


# --------------------------------- Rotas -------------------------------------
@router_auth.post("/api/v1/auth/login", response_model=TokenPair)
def login(req: LoginRequest):
    """
    Valida usuário/senha simples (DEMO) e emite par de tokens (access + refresh).
    Em produção, substitua por validação real e leia credenciais de um banco.
    """
    if not (req.username == DEMO_USER and req.password == DEMO_PASS):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access = create_access_token(req.username)
    refresh = create_refresh_token(req.username)
    return TokenPair(access_token=access, refresh_token=refresh)


@router_auth.post("/api/v1/auth/refresh", response_model=TokenPair)
def refresh(req: RefreshRequest):
    """
    Recebe um refresh_token válido e devolve novo access_token.
    Mantém/renova também um novo refresh_token simples (padrão).
    """
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Token não é de refresh")

    username = payload.get("sub")
    access = create_access_token(username)
    # opcional: emitir novo refresh para estender sessão
    refresh_token = create_refresh_token(username)
    return TokenPair(access_token=access, refresh_token=refresh_token)
# --- Dependência para proteger rotas com Bearer token ---
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_security = HTTPBearer()

def require_user(credentials: HTTPAuthorizationCredentials = Depends(_security)):
    """
    Lê o header Authorization: Bearer <access_token>, valida o JWT e retorna o usuário.
    """
    token = credentials.credentials
    payload = decode_token(token)
    if payload.get("type") != "access":
        # só aceitamos access token nesta rota
        raise HTTPException(status_code=401, detail="Token não é de acesso")
    return {"username": payload.get("sub")}
