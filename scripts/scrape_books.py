# Importa a biblioteca requests para fazer requisições HTTP (baixar páginas da web).
import requests
# Importa o BeautifulSoup para "parsear" (analisar/ler) o HTML e conseguir extrair elementos.
from bs4 import BeautifulSoup
# Importa o pandas para organizar os dados em tabela (DataFrame) e salvar em CSV.
import pandas as pd


# Define a função principal que fará todo o processo de scraping e geração do CSV.
def scrape_books():
    # URL base das páginas de catálogo do site (parte comum usada para montar as URLs).
    base_url = "https://books.toscrape.com/catalogue/"
    # Primeira página do catálogo (ponto de partida do scraping).
    start_url = base_url + "page-1.html"
    # Lista vazia que armazenará um dicionário por livro coletado.
    books = []

    # Variável de controle do loop de paginação: começamos na primeira página.
    url = start_url
    # Enquanto houver uma URL válida de página, continuamos extraindo dados.
    while url:
        # Apenas imprime no terminal qual página está sendo processada (útil para acompanhar o progresso).
        print(f"Scraping: {url}")
        # Faz a requisição HTTP para obter o HTML da página de catálogo atual.
        response = requests.get(url)
        # Cria o objeto BeautifulSoup a partir do HTML retornado, usando o parser padrão 'html.parser'.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Seleciona todos os cards de produto (cada livro) dentro da página de catálogo.
        for article in soup.select("article.product_pod"):
            # Extrai o título do livro a partir do elemento <h3><a title="..."></a></h3>.
            title = article.h3.a['title']

            # Captura o preço bruto exibido no card (com símbolo de moeda e possível encoding estranho).
            price_raw = article.select_one(".price_color").text.strip()
            # Corrige o encoding (latin1 -> utf-8) e substitui o símbolo de libra (£) por "R$ ".
            # Observação: aqui apenas trocamos o símbolo; não há conversão de moeda.
            price = price_raw.encode('latin1').decode('utf-8').replace("£", "R$ ")

            # Extrai o texto de disponibilidade (ex.: "In stock").
            availability = article.select_one(".availability").text.strip()

            # Extrai a classe de rating do elemento <p class="star-rating ..."> (ex.: One, Two, Three, Four, Five).
            rating = article.p['class'][1]

            # Pega o link relativo da página de detalhes do livro a partir do <h3><a href="..."></a></h3>.
            link = article.h3.a['href']
            # Monta a URL completa da página de detalhes, concatenando com a base do catálogo.
            detail_url = base_url + link

            # Faz uma nova requisição HTTP para a página de detalhes do livro (para pegar categoria e imagem).
            detail_response = requests.get(detail_url)
            # Cria um BeautifulSoup para a página de detalhes.
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

            # Localiza o "breadcrumb" (trilha de navegação) e seleciona todos os links dentro dele.
            breadcrumb = detail_soup.select("ul.breadcrumb li a")
            # Pega o último link do breadcrumb como categoria (depende da estrutura do site; funcionou nos testes).
            # Se não encontrar breadcrumb, define "Unknown".
            category = breadcrumb[-1].text.strip() if breadcrumb else "Unknown"

            # Seleciona a tag <img> da galeria de imagens do produto na página de detalhes.
            img_tag = detail_soup.select_one(".item.active img")
            # Monta a URL absoluta da imagem, removendo "../" do caminho relativo. Se não houver imagem, usa string vazia.
            img_url = "https://books.toscrape.com/" + img_tag['src'].replace("../", "") if img_tag else ""

            # Adiciona um dicionário com todos os campos do livro à lista 'books'.
            books.append({
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "category": category,
                "image_url": img_url
            })

        # Após processar todos os livros da página, tentamos descobrir se existe uma próxima página.
        next_button = soup.select_one("li.next a")
        if next_button:
            # Se existir, pega o href (ex.: "page-2.html") e monta a próxima URL completa.
            next_page = next_button['href']
            url = base_url + next_page
        else:
            # Se não existir próxima página, define url como None para encerrar o loop.
            url = None

    # Converte a lista de dicionários 'books' em um DataFrame pandas (tabela em memória).
    df = pd.DataFrame(books)
    # Salva o DataFrame no arquivo CSV dentro da pasta data/, sem índice e com encoding UTF-8.
    df.to_csv("data/books.csv", index=False, encoding='utf-8')
    # Mensagem final no terminal confirmando que o arquivo foi gerado com sucesso.
    print("✅ Arquivo salvo com sucesso em data/books.csv")


# Este bloco garante que a função scrape_books() só rode automaticamente
# quando este arquivo for executado diretamente (python scripts/scrape_books.py),
# e NÃO quando o arquivo for apenas importado por outro módulo.
if __name__ == "__main__":
    # Chama a função principal para iniciar o scraping.
    scrape_books()
