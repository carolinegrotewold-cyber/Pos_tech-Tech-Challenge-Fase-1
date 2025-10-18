from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Rotas públicas da API (books, categories, stats, health)
from api.routes import router
# Rotas de autenticação (login/refresh)
from api.auth import router_auth
from api.admin import router_admin

# Cria a aplicação com título (apenas uma vez)
app = FastAPI(title="CGROTEWO - Books API")

# CORS (liberado em dev; em produção, restrinja allow_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ex.: ["https://seu-front.com"] em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os routers
app.include_router(router)       # endpoints públicos (/api/v1/books, /categories, /stats, /health)
app.include_router(router_auth)  # auth (/api/v1/auth/login, /api/v1/auth/refresh)
app.include_router(router_admin)

