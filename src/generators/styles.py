"""Estilos ABNT para documentos DOCX.

Define todos os estilos de parágrafo e caractere conforme as normas ABNT,
aplicáveis via python-docx.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from src.core.config import Formatacao


@dataclass
class EstiloParagrafo:
    """Configuração de estilo de parágrafo."""

    nome: str
    fonte: str = Formatacao.FONTE_PADRAO
    tamanho: int = Formatacao.TAMANHO_FONTE
    espacamento: float = Formatacao.ESPACAMENTO_LINHAS
    alinhamento: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY
    negrito: bool = False
    italico: bool = False
    indentacao_esquerda: float | None = None  # cm
    indentacao_primeira_linha: float | None = None  # cm
    espaco_antes: int = 0  # pt
    espaco_depois: int = 0  # pt
    maiusculas: bool = False


# ── Estilos pré-definidos ───────────────────────────────────────────────────

ESTILO_CORPO = EstiloParagrafo(
    nome="Corpo ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=Formatacao.ESPACAMENTO_LINHAS,
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indentacao_primeira_linha=Formatacao.INDENTACAO_PRIMEIRA_LINHA,
)

ESTILO_TITULO_NIVEL_1 = EstiloParagrafo(
    nome="Título 1 ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=Formatacao.ESPACAMENTO_LINHAS,
    alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
    negrito=True,
    maiusculas=True,
    espaco_antes=24,
    espaco_depois=12,
)

ESTILO_TITULO_NIVEL_2 = EstiloParagrafo(
    nome="Título 2 ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=Formatacao.ESPACAMENTO_LINHAS,
    alinhamento=WD_ALIGN_PARAGRAPH.LEFT,
    negrito=True,
    maiusculas=True,
    espaco_antes=18,
    espaco_depois=12,
)

ESTILO_TITULO_NIVEL_3 = EstiloParagrafo(
    nome="Título 3 ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=Formatacao.ESPACAMENTO_LINHAS,
    alinhamento=WD_ALIGN_PARAGRAPH.LEFT,
    negrito=True,
    espaco_antes=12,
    espaco_depois=6,
)

ESTILO_TITULO_NIVEL_4 = EstiloParagrafo(
    nome="Título 4 ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=Formatacao.ESPACAMENTO_LINHAS,
    alinhamento=WD_ALIGN_PARAGRAPH.LEFT,
    negrito=True,
    italico=True,
    espaco_antes=12,
    espaco_depois=6,
)

ESTILO_CITACAO_LONGA = EstiloParagrafo(
    nome="Citação longa ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=10,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indentacao_esquerda=4.0,
    indentacao_primeira_linha=0,
)

ESTILO_REFERENCIA = EstiloParagrafo(
    nome="Referência ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indentacao_esquerda=0,
    indentacao_primeira_linha=0,
)

ESTILO_LEGENDA = EstiloParagrafo(
    nome="Legenda ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
)

ESTILO_NUMERO_PAGINA = EstiloParagrafo(
    nome="Numeração ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
)

ESTILO_RESUMO = EstiloParagrafo(
    nome="Resumo ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

ESTILO_CAPA = EstiloParagrafo(
    nome="Capa ABNT",
    fonte=Formatacao.FONTE_PADRAO,
    tamanho=Formatacao.TAMANHO_FONTE,
    espacamento=1.0,
    alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
)

# ── Mapa de estilos por nível ───────────────────────────────────────────────

ESTILOS_TITULO: dict[int, EstiloParagrafo] = {
    1: ESTILO_TITULO_NIVEL_1,
    2: ESTILO_TITULO_NIVEL_2,
    3: ESTILO_TITULO_NIVEL_3,
    4: ESTILO_TITULO_NIVEL_4,
}