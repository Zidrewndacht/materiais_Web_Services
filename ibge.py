import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Como tornar essas três funções uma só?
def buscar_estado():
    "Busca lista de estados no IBGE usando API de localidades: "
    "https://servicodados.ibge.gov.br/api/v1/localidades"

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados" 
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Erro ao buscar estado: {e}[/red]")
        return None

def buscar_municipio(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios" 
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Erro ao buscar estado: {e}[/red]")
        return None

def buscar_dados_muni(id):  
    # e se fosse buscar por nome? 
    # Verifique processamento de nomes como Pérola D'Oeste
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{id}" 
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Erro ao buscar estado: {e}[/red]")
        return None


#Como proteger de erros de valores inválidos digitados pelo usuário?

def main():
    console.print("[bold cyan]Carregando estados...[/bold cyan]")
    estados = buscar_estado()

    tabela_estados = Table(title="Estados")
    tabela_estados.add_column("Sigla", style="magenta", no_wrap=True)
    tabela_estados.add_column("Nome", style="green", no_wrap=True)
    tabela_estados.add_column("Região", style="cyan", no_wrap=True)

    for estado in estados:
        tabela_estados.add_row(
            estado.get("sigla"), 
            estado.get("nome"), 
            estado.get("regiao",{}).get("nome"))
        
    console.print(tabela_estados)

    entrada_estado = console.input("Digite a sigla do estado: ").strip().upper()

    console.print(f"[bold cyan]Carregando municípios de {entrada_estado}[/bold cyan]")
    municipios = buscar_municipio(entrada_estado)

    tabela_muni = Table(title=f"Municípios de {entrada_estado}")
    tabela_muni.add_column("ID", style="yellow",no_wrap=True)
    tabela_muni.add_column("Nome", style="cyan",no_wrap=True)

    for municipio in municipios:
        tabela_muni.add_row( str(municipio.get("id")) , municipio.get("nome") )

    console.print(tabela_muni)
    
    entrada_id = console.input("Digite a [bold cyan]ID[/bold cyan] do município: ").strip()
    console.print(f"[bold cyan]Carregando dados de município ID {entrada_id}[/bold cyan]")

    dados_muni = buscar_dados_muni(entrada_id)

    nome = dados_muni.get("nome")
    meso =  dados_muni.get("microrregiao",{}).get("mesorregiao",{}).get("nome")
    reg_imediata =  dados_muni.get("regiao-imediata",{}).get("nome")

    texto_painel=(
        f"[bold]Nome:[/bold] {nome}"   
        f"[bold]Mesorregião:[/bold] {meso}"   
        f"[bold]Região Imediata:[/bold] {reg_imediata}"   
    )

    painel = Panel(texto_painel, title=f"Detalhes de {nome}",border_style="blue")
    console.print(painel)

if __name__ == "__main__":
    main()