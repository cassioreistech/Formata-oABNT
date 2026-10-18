"""CLI principal do Formata-oABNT.

Interface de linha de comando para formatação de documentos acadêmicos.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src import __version__

app = typer.Typer(
    name="formata-abnt",
    help="🎓 Sistema premium de formatação automática de documentos ABNT",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"Formata-oABNT v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True
    ),
) -> None:
    """Sistema premium de formatação ABNT."""


@app.command()
def formatar(
    arquivo: Path = typer.Argument(..., help="Arquivo JSON/YAML com os dados do documento"),
    formato: str = typer.Option("docx", "--formato", "-f", help="Formato de saída (docx/pdf)"),
    saida: Path = typer.Option(None, "--saida", "-o", help="Caminho do arquivo de saída"),
    sem_validacao: bool = typer.Option(False, "--sem-validacao", help="Pular validação"),
) -> None:
    """Formata um documento acadêmico conforme normas ABNT."""
    import json

    import yaml

    from src.core.engine import Engine
    from src.core.models import Documento

    if not arquivo.exists():
        console.print(f"[red]Arquivo não encontrado: {arquivo}[/red]")
        raise typer.Exit(1)

    # Carregar dados
    try:
        conteudo = arquivo.read_text(encoding="utf-8")
        if arquivo.suffix in (".yaml", ".yml"):
            dados = yaml.safe_load(conteudo)
        else:
            dados = json.loads(conteudo)
    except Exception as e:
        console.print(f"[red]Erro ao ler arquivo: {e}[/red]")
        raise typer.Exit(1)

    # Criar documento
    try:
        documento = Documento(**dados)
    except Exception as e:
        console.print(f"[red]Erro nos dados do documento: {e}[/red]")
        raise typer.Exit(1)

    # Formatar
    engine = Engine()
    try:
        caminho = engine.formatar(
            documento=documento,
            formato=formato,
            caminho_saida=saida,
            validar=not sem_validacao,
        )
        console.print(
            Panel(
                f"[green]✅ Documento gerado com sucesso![/green]\n"
                f"📄 Arquivo: [bold]{caminho}[/bold]\n"
                f"📋 Formato: {formato.upper()}",
                title="Formata-oABNT",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[red]Erro ao formatar: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def modelo(
    tipo: str = typer.Argument("tcc", help="Tipo de documento (tcc/artigo/dissertacao/tese/relatorio)"),
    saida: Path = typer.Option(None, "--saida", "-o", help="Caminho do arquivo de modelo"),
) -> None:
    """Gera um modelo/template para preenchimento."""
    import json

    from src.core.config import TipoDocumento

    modelos = {
        "tcc": _modelo_tcc(),
        "artigo": _modelo_artigo(),
        "dissertacao": _modelo_dissertacao(),
        "tese": _modelo_tese(),
        "relatorio": _modelo_relatorio(),
    }

    if tipo not in modelos:
        console.print(f"[red]Tipo não suportado: {tipo}[/red]")
        console.print(f"Tipos disponíveis: {', '.join(modelos.keys())}")
        raise typer.Exit(1)

    modelo_dados = modelos[tipo]

    if saida is None:
        saida = Path(f"modelo_{tipo}.json")

    saida.write_text(
        json.dumps(modelo_dados, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    console.print(f"[green]✅ Modelo gerado: {saida}[/green]")


@app.command()
def info() -> None:
    """Mostra informações sobre as normas ABNT cobertas."""
    table = Table(title="📋 Normas ABNT Cobertas", show_lines=True)
    table.add_column("Norma", style="cyan bold")
    table.add_column("Descrição", style="white")
    table.add_column("Status", style="green")

    normas = [
        ("NBR 14724", "Trabalhos acadêmicos — Estrutura e formatação", "✅"),
        ("NBR 6023", "Referências bibliográficas", "✅"),
        ("NBR 6024", "Numeração progressiva das seções", "✅"),
        ("NBR 6027", "Sumário", "✅"),
        ("NBR 6028", "Resumo e palavras-chave", "✅"),
        ("NBR 10520", "Citações no texto", "✅"),
        ("NBR 15287", "Projetos de pesquisa", "✅"),
    ]

    for norma, desc, status in normas:
        table.add_row(norma, desc, status)

    console.print(table)


# ── Modelos de exemplo ──────────────────────────────────────────────────────


def _modelo_tcc() -> dict:
    return {
        "metadados": {
            "titulo": "Título do Trabalho",
            "subtitulo": "Subtítulo (opcional)",
            "autores": [
                {
                    "nome_completo": "Nome Completo do Autor",
                    "afiliacao": "Universidade XYZ",
                }
            ],
            "tipo": "tcc",
            "instituicao": "Nome da Universidade",
            "curso": "Nome do Curso",
            "cidade": "Cidade",
            "estado": "UF",
            "ano": 2024,
            "orientador": "Nome do Orientador",
            "palavras_chave": ["palavra1", "palavra2", "palavra3"],
        },
        "resumo": "Texto do resumo aqui...",
        "abstract": "Abstract text here...",
        "secoes": [
            {
                "titulo": "Introdução",
                "nivel": 1,
                "conteudo": [
                    "Primeiro parágrafo da introdução...",
                    "Segundo parágrafo...",
                ],
            },
            {
                "titulo": "Revisão Bibliográfica",
                "nivel": 1,
                "conteudo": ["Conteúdo da revisão..."],
                "subsecoes": [
                    {
                        "titulo": "Tema Específico",
                        "nivel": 2,
                        "conteudo": ["Conteúdo da subseção..."],
                    }
                ],
            },
            {
                "titulo": "Metodologia",
                "nivel": 1,
                "conteudo": ["Descrição da metodologia..."],
            },
            {
                "titulo": "Resultados e Discussão",
                "nivel": 1,
                "conteudo": ["Apresentação dos resultados..."],
            },
            {
                "titulo": "Conclusão",
                "nivel": 1,
                "conteudo": ["Considerações finais..."],
            },
        ],
        "referencias": [
            {
                "tipo": "livro",
                "autores": ["SOBRENOME, Nome"],
                "titulo": "Título do Livro",
                "edicao": "2",
                "local": "Cidade",
                "editora": "Editora",
                "ano": 2023,
            }
        ],
    }


def _modelo_artigo() -> dict:
    return {
        "metadados": {
            "titulo": "Título do Artigo",
            "autores": [{"nome_completo": "Nome do Autor"}],
            "tipo": "artigo",
            "instituicao": "Universidade",
            "cidade": "Cidade",
            "ano": 2024,
            "palavras_chave": ["chave1", "chave2"],
        },
        "resumo": "Resumo do artigo...",
        "secoes": [
            {"titulo": "Introdução", "nivel": 1, "conteudo": ["..."]},
            {"titulo": "Materiais e Métodos", "nivel": 1, "conteudo": ["..."]},
            {"titulo": "Resultados", "nivel": 1, "conteudo": ["..."]},
            {"titulo": "Discussão", "nivel": 1, "conteudo": ["..."]},
            {"titulo": "Conclusão", "nivel": 1, "conteudo": ["..."]},
        ],
        "referencias": [],
    }


def _modelo_dissertacao() -> dict:
    modelo = _modelo_tcc()
    modelo["metadados"]["tipo"] = "dissertacao"
    modelo["metadados"]["area_concentracao"] = "Área de Concentração"
    return modelo


def _modelo_tese() -> dict:
    modelo = _modelo_tcc()
    modelo["metadados"]["tipo"] = "tese"
    modelo["metadados"]["area_concentracao"] = "Área de Concentração"
    return modelo


def _modelo_relatorio() -> dict:
    modelo = _modelo_tcc()
    modelo["metadados"]["tipo"] = "relatorio"
    return modelo


if __name__ == "__main__":
    app()