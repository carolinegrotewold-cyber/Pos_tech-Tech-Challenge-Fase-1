from fastapi import APIRouter
import pandas as pd

router = APIRouter()

# ---------------------------
# /api/v1/books  → lista todos os livros
# ---------------------------
@router.get("/api/v1/books")
def get_books():
    try:
        df = pd.read_csv("data/books.csv")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao listar livros: {str(e)}"}


# ---------------------------
# /api/v1/books/search  → busca por título e/ou categoria
# ---------------------------
@router.get("/api/v1/books/search")
def search_books(title: str = "", category: str = ""):
    """
    Ex.: /api/v1/books/search?title=light&category=Poetry
    """
    try:
        df = pd.read_csv("data/books.csv")

        if title:
            df = df[df["title"].str.contains(title, case=False, na=False)]

        if category:
            df = df[df["category"].str.contains(category, case=False, na=False)]

        return df.to_dict(orient="records")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao buscar livros: {str(e)}"}


# ---------------------------
# /api/v1/books/top-rated  → livros com melhor avaliação
# ---------------------------
@router.get("/api/v1/books/top-rated")
def books_top_rated(limit: int = 10, min_rating: int = 4):
    """
    Retorna os livros com melhor avaliação.
    - limit: quantidade (padrão 10)
    - min_rating: mínimo 1..5 (padrão 4 → 'Four' e 'Five')
    """
    try:
        df = pd.read_csv("data/books.csv")

        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        df["rating_num"] = df["rating"].map(rating_map).fillna(0).astype(int)

        # valida min_rating
        if min_rating < 1:
            min_rating = 1
        if min_rating > 5:
            min_rating = 5

        df = df[df["rating_num"] >= int(min_rating)]
        df = df.sort_values(by=["rating_num", "title"], ascending=[False, True]).head(int(limit))
        df = df.drop(columns=["rating_num"], errors="ignore")

        return df.to_dict(orient="records")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao obter top-rated: {str(e)}"}

# ---------------------------
# /api/v1/books/price-range  → filtra por faixa de preço (R$)
# ---------------------------
@router.get("/api/v1/books/price-range")
def books_price_range(min: float = 0.0, max: float = 1e12):
    """
    Filtra livros cujo preço (R$) esteja entre min e max (inclusive).
    Exemplos:
      /api/v1/books/price-range?min=30&max=50
      /api/v1/books/price-range?max=25
      /api/v1/books/price-range?min=60
    """
    try:
        df = pd.read_csv("data/books.csv")

        # Converte "R$ 44.48" -> 44.48 (float)
        df["preco_float"] = (
            df["price"]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.strip()
            .astype(float)
        )

        # Validações simples
        if min < 0 or max < 0:
            return {"status": "error", "message": "min e max devem ser não-negativos."}
        if min > max:
            return {"status": "error", "message": "min não pode ser maior que max."}

        # Aplica filtro e ordena pelo preço crescente
        mask = (df["preco_float"] >= float(min)) & (df["preco_float"] <= float(max))
        df = df.loc[mask].copy().sort_values(by="preco_float", ascending=True)

        # Remove coluna auxiliar e retorna JSON
        df = df.drop(columns=["preco_float"], errors="ignore")
        return df.to_dict(orient="records")

    except Exception as e:
        return {"status": "error", "message": f"Erro ao filtrar por faixa de preço: {str(e)}"}



# ---------------------------
# /api/v1/books/{book_id}  → detalhe por índice (DEIXAR DEPOIS das rotas fixas)
# ---------------------------
@router.get("/api/v1/books/{book_id}")
def get_book_by_id(book_id: int):
    try:
        df = pd.read_csv("data/books.csv")

        if book_id < 0 or book_id >= len(df):
            return {"error": f"Livro com ID {book_id} não encontrado"}

        return df.iloc[int(book_id)].to_dict()
    except Exception as e:
        return {"status": "error", "message": f"Erro interno: {str(e)}"}


# ---------------------------
# /api/v1/categories  → lista categorias únicas (ordenadas)
# ---------------------------
@router.get("/api/v1/categories")
def get_categories():
    try:
        df = pd.read_csv("data/books.csv")
        categories = df["category"].dropna().unique().tolist()
        categories.sort()
        return {"categories": categories}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao carregar categorias: {str(e)}"}


# ---------------------------
# /api/v1/health  → status da API e dos dados
# ---------------------------
@router.get("/api/v1/health")
def health_check():
    try:
        df = pd.read_csv("data/books.csv")
        return {
            "status": "ok",
            "message": "API funcionando",
            "books_loaded": int(len(df)),
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao acessar os dados: {str(e)}"}


# ---------------------------
# /api/v1/stats/overview  → estatísticas gerais
# ---------------------------
@router.get("/api/v1/stats/overview")
def stats_overview():
    """
    total de livros, preço médio (R$) e distribuição de ratings
    """
    try:
        df = pd.read_csv("data/books.csv")
        total_books = len(df)

        # "R$ " → remove símbolo e espaços; converte para float
        df["preco_float"] = (
            df["price"].astype(str).str.replace("R$", "", regex=False).str.strip().astype(float)
        )

        media_precos = round(df["preco_float"].mean(), 2)
        ratings = df["rating"].value_counts().to_dict()

        return {
            "total_books": int(total_books),
            "average_price_brl": f"R${media_precos:.2f}",
            "rating_distribution": ratings,
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao calcular estatísticas: {str(e)}"}


# ---------------------------
# /api/v1/stats/categories  → estatísticas por categoria
# ---------------------------
@router.get("/api/v1/stats/categories")
def stats_by_category():
    """
    Para cada categoria: quantidade e preço médio (R$)
    """
    try:
        df = pd.read_csv("data/books.csv")
        df["preco_float"] = (
            df["price"].astype(str).str.replace("R$", "", regex=False).str.strip().astype(float)
        )

        resumo = (
            df.groupby("category")
              .agg(book_count=("title", "count"), average_price_brl=("preco_float", "mean"))
              .reset_index()
        )

        resumo["average_price_brl"] = resumo["average_price_brl"].round(2)
        resumo["average_price_brl"] = resumo["average_price_brl"].apply(lambda x: f"R${x:.2f}")

        return resumo.to_dict(orient="records")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao calcular estatísticas por categoria: {str(e)}"}
