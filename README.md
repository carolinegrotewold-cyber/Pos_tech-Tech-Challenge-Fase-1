# Projeto CGROTEWO - API de Livros

## Descrição
API para extração, transformação e consulta de livros via web scraping no site https://books.toscrape.com.

## Como rodar localmente

```bash
git clone [repo]
cd CGROTEWO
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/scrape_books.py
uvicorn main:app --reload
