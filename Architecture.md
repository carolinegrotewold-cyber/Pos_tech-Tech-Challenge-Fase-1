Arquitetura — CGROTEWO (Books API)

URL pública:** https://cgrotewold.onrender.com  
Docs (Swagger):** https://cgrotewold.onrender.com/docs

API em **FastAPI** que realiza **web scraping** no *Books to Scrape*, persiste em **CSV** e expõe endpoints de consulta, busca, estatísticas e administração (**JWT**).

---

1) Visão Geral

```mermaid
flowchart LR
    A[Books to Scrape] -->|HTTP GET| B[Scraper (requests + BeautifulSoup)]
    B --> C[(CSV: data/books.csv)]
    C --> D[FastAPI - Endpoints Públicos]
    C --> E[FastAPI - Estatísticas]
    D --> F[Clientes: Swagger / cURL / Frontend]
    E --> F
    G[Auth (JWT)] --> H[/api/v1/scraping/trigger (protegido)]
    H --> B


Fluxo resumido
1. Scraper baixa e parseia os livros (título, preço, disponibilidade, rating, categoria, imagem).
2. Dados são salvos em data/books.csv.
3. API lê o CSV sob demanda e expõe endpoints REST.
4. JWT protege a rota administrativa de re-scraping.


2) Componentes

CGROTEWO/
├─ api/
│  ├─ routes.py   # endpoints públicos (books, search, price-range, top-rated, categories, stats, health)
│  ├─ auth.py     # /auth/login, /auth/refresh e require_user (HTTPBearer/JWT)
│  └─ admin.py    # /scraping/trigger (protegida)
├─ scripts/
│  ├─ scrape_books.py  # scraping (requests + bs4) → data/books.csv
│  └─ __init__.py
├─ data/books.csv       # dataset raspado
├─ main.py              # app FastAPI, CORS e inclusão dos routers
├─ requirements.txt
└─ README.md
Decisões
* CSV como armazenamento: simples e suficiente para o escopo; facilita o consumo por ciência de dados.
* Leitura sob demanda: evita estado em memória e garante dados atualizados após novo scraping.
* Separação clara: scraping (scripts), rotas públicas (routes), auth (auth), admin (admin).


3) Endpoints e Contratos

classDiagram
    class BooksAPI{
      +GET /api/v1/books
      +GET /api/v1/books/{book_id}
      +GET /api/v1/books/search?title=&category=
      +GET /api/v1/books/price-range?min=&max=
      +GET /api/v1/books/top-rated?limit=&min_rating=
      +GET /api/v1/categories
      +GET /api/v1/stats/overview
      +GET /api/v1/stats/categories
      +GET /api/v1/health
    }
    class AuthAPI{
      +POST /api/v1/auth/login
      +POST /api/v1/auth/refresh
    }
    class AdminAPI{
      +POST /api/v1/scraping/trigger?sync={true|false}
    }
Observações de implementação
* Ordem de rotas /books: rotas fixas (/search, /price-range, /top-rated) vêm antes de /{book_id} para evitar conflito.
* price-range: converte "R$ 44.48" → 44.48 (float) e ordena crescente.
* top-rated: mapeia One..Five → 1..5, filtra por min_rating e limita por limit.
* stats: overview (total, preço médio, distribuição de ratings) e por categoria (quantidade, preço médio).
* health: indica disponibilidade e total de livros carregados.



4) Autenticação e Segurança (JWT)
* PyJWT (HS256): access_token (~30 min) e refresh_token (~7 dias).
* Proteção via HTTPBearer + require_user em rotas sensíveis (/scraping/trigger).
* Swagger “Authorize”: colar apenas o access_token no modal.


5) Deploy (Render)
* Build: pip install -r requirements.txt
* Start: uvicorn main:app --host 0.0.0.0 --port $PORT
* Secrets recomendados: JWT_SECRET=<valor-seguro>
* Testes após deploy:
    * Docs: https://cgrotewold.onrender.com/docs
    * Health: https://cgrotewold.onrender.com/api/v1/health

6) Observabilidade / Confiabilidade
* Logs simples no scraper e respostas de erro tratadas nos endpoints.
* /health para verificação de disponibilidade e contagem de registros.
* (Evoluções possíveis) logging estruturado, métricas e tracing.

7) Escalabilidade e Roadmap
* Persistência: migrar CSV → SQLite/Postgres para concorrência/escala.
* Desempenho: cache em endpoints de leitura frequente.
* Agendamento: cron (Render Scheduler/GitHub Actions) para scraping periódico.
* Testes: adicionar suite pytest para rotas críticas.
* UI: painel (ex.: Streamlit) consumindo a API.
