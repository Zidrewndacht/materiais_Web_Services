import requests
import unicodedata
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"

def buscar_dados(endpoint):
    """Função unificada para buscar dados da API do IBGE."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Erro ao buscar dados: {e}[/red]")
        return None


def normalizar_nome(nome):
    """Normaliza o nome do município para URL amigável."""
    texto = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.lower()
    texto = texto.replace(' ', '-')
    texto = re.sub(r'[^a-z0-9-]', '', texto)
    texto = re.sub(r'-+', '-', texto)
    return texto


def main():
    # Carregar Estados
    console.print("[bold cyan]Carregando estados...[/bold cyan]")
    estados = buscar_dados("estados")
    
    if not estados:
        console.print("[red]Não foi possível carregar a lista de estados.[/red]")
        return
    
    tabela_estados = Table(title="Estados")
    tabela_estados.add_column("Sigla", style="magenta", no_wrap=True)
    tabela_estados.add_column("Nome", style="green", no_wrap=True)
    tabela_estados.add_column("Região", style="cyan", no_wrap=True)
    
    for estado in estados:
        tabela_estados.add_row(
            estado.get("sigla"),
            estado.get("nome"),
            estado.get("regiao", {}).get("nome")
        )
    
    console.print(tabela_estados)
    
    # Selecionar Estado
    while True:
        entrada_estado = console.input("Digite a sigla do estado: ").strip().upper()
        if any(e.get("sigla") == entrada_estado for e in estados):
            break
        console.print("[red]Sigla inválida. Tente novamente.[/red]")
    
    # Carregar Municípios
    console.print(f"[bold cyan]Carregando municípios de {entrada_estado}[/bold cyan]")
    municipios = buscar_dados(f"estados/{entrada_estado}/municipios")
    
    if not municipios:
        console.print("[red]Não foi possível carregar os municípios.[/red]")
        return
    
    tabela_muni = Table(title=f"Municípios de {entrada_estado}")
    tabela_muni.add_column("ID", style="yellow", no_wrap=True)
    tabela_muni.add_column("Nome", style="cyan", no_wrap=True)
    
    for municipio in municipios:
        tabela_muni.add_row(str(municipio.get("id")), municipio.get("nome"))
    
    console.print(tabela_muni)
    
    # Selecionar Município (ID ou Nome)
    entrada_muni = console.input("Digite a ID ou Nome do município: ").strip()
    
    entrada_sanitizada = normalizar_nome(entrada_muni)
    
    # Buscar dados
    console.print(f"[bold cyan]Carregando dados de município {entrada_muni}[/bold cyan]")
    dados_muni = buscar_dados(f"municipios/{entrada_sanitizada}")
    
    if not dados_muni:
        console.print("[red]Município não encontrado.[/red]")
        return
    
    # Acessar diretamente como dicionário (igual ao código original)
    nome = dados_muni.get("nome")
    meso = dados_muni.get("microrregiao", {}).get("mesorregiao", {}).get("nome")
    reg_imediata = dados_muni.get("regiao-imediata", {}).get("nome")
    
    texto_painel = (
        f"[bold]Nome:[/bold] {nome}\n"
        f"[bold]Mesorregião:[/bold] {meso}\n"
        f"[bold]Região Imediata:[/bold] {reg_imediata}"
    )
    
    painel = Panel(texto_painel, title=f"Detalhes de {nome}", border_style="blue")
    console.print(painel)


if __name__ == "__main__":
    main()