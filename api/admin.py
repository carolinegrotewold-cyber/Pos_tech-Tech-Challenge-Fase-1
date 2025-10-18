from fastapi import APIRouter, Depends, BackgroundTasks
from api.auth import require_user
from scripts.scrape_books import scrape_books  # garante que 'scripts' é importável
import pandas as pd

router_admin = APIRouter()

@router_admin.post("/api/v1/scraping/trigger")
def trigger_scraping(background_tasks: BackgroundTasks, sync: bool = False, user=Depends(require_user)):
    """
    Dispara o scraping:
      - sync=false (padrão): roda em background e responde rápido.
      - sync=true: roda sincrono e retorna um resumo ao final.
    Exemplo:
      POST /api/v1/scraping/trigger          -> background
      POST /api/v1/scraping/trigger?sync=true -> síncrono
    """
    if sync:
        # Executa o scraping agora e devolve estatísticas
        scrape_books()
        df = pd.read_csv("data/books.csv")
        return {
            "status": "ok",
            "message": "Scraping concluído",
            "books_loaded": int(len(df)),
            "requested_by": user["username"],
            "mode": "sync"
        }
    else:
        # Agenda a execução e responde imediatamente
        background_tasks.add_task(scrape_books)
        return {
            "status": "started",
            "message": "Scraping iniciado em background",
            "requested_by": user["username"],
            "mode": "background"
        }
