# CGROTEWO — Books API

URL pública:** https://cgrotewold.onrender.com  
Docs (Swagger):** https://cgrotewold.onrender.com/docs

API em **FastAPI** que raspa o site **Books to Scrape**, salva em CSV e expõe rotas de consulta, busca, estatísticas e administração (JWT).

```bash
# criar venv e instalar
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# gerar CSV (scraping)
python scripts/scrape_books.py

# subir API
uvicorn main:app --reload --port 8002
# docs: http://127.0.0.1:8002/docs
🔐 Autenticação (JWT)
Login: POST /api/v1/auth/login

json
Copy code
{ "username": "admin", "password": "admin123" }
→ retorna access_token e refresh_token.

Refresh: POST /api/v1/auth/refresh

No Swagger: clique Authorize e cole apenas o access_token.

## Endpoints (base = https://cgrotewold.onrender.com)

Públicos

GET /api/v1/health

GET /api/v1/books

GET /api/v1/books/{book_id}

GET /api/v1/books/search?title=&category=

GET /api/v1/books/price-range?min=&max=

GET /api/v1/books/top-rated?limit=&min_rating=

GET /api/v1/categories

GET /api/v1/stats/overview

GET /api/v1/stats/categories

Protegido (JWT)

POST /api/v1/scraping/trigger?sync={true|false}
Header: Authorization: Bearer <access_token>

## Exemplos (cURL) — URL pública
bash
Copy code
# saúde
curl -s https://cgrotewold.onrender.com/api/v1/health | jq .

# top 5 nota 5
curl -s "https://cgrotewold.onrender.com/api/v1/books/top-rated?limit=5&min_rating=5" | jq .

# faixa de preço
curl -s "https://cgrotewold.onrender.com/api/v1/books/price-range?min=30&max=40" | jq '.[0:5]'

# login (pegar tokens)
curl -s -X POST https://cgrotewold.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq .

# trigger protegido (background)
ACCESS="<access_token_aqui>"
curl -s -X POST https://cgrotewold.onrender.com/api/v1/scraping/trigger \
  -H "Authorization: Bearer $ACCESS" | jq .

## Estrutura
css
Copy code
api/ (routes.py, auth.py, admin.py)
scripts/ (scrape_books.py)
data/ (books.csv)
main.py
requirements.txt

## Deploy (Render)
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT


## Troubleshooting
404 na raiz / → use /docs ou /api/v1/health.

401 em rota protegida → refaça login, Authorize no Swagger e use o access_token.

ARCHITECTURE.md —> Para ver a arquitetura 

——————————————————————————————————————————————————
