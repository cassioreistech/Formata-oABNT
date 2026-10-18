"""Detecção e formatação de citações diretas longas (NBR 10520)."""

from __future__ import annotations

import math

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

from formata_abnt.estilos import obter_ou_criar_estilo_citacao
from formata_abnt.normas import NormasABNT
from formata_abnt.runs import definir_fonte
from formata_abnt.titulos import nivel_do_titulo

_MARCADORES_INICIAIS = ('"', "“", "”", "«", ">")
_MARCADORES_FINAIS = ('"', "“", "”", "»")


def estimar_linhas(texto: str, caracteres_por_linha: int = 65) -> int:
    """Estima o número de linhas que o texto ocupa na largura ABNT."""
    texto = texto.strip()
    if not texto:
        return 0
    return max(1, math.ceil(len(texto) / caracteres_por_linha))


def parece_citacao_direta(texto: str) -> bool:
    """Indica se o texto tem indício de citação direta (aspas ou marcador)."""
    recortado = texto.strip()
    if not recortado:
        return False
    return recortado.startswith(_MARCADORES_INICIAIS) or recortado.endswith(
        _MARCADORES_FINAIS
    )


def eh_citacao_longa(paragrafo: Paragraph, normas: NormasABNT) -> bool:
    """Decide se o parágrafo é uma citação direta com mais de três linhas."""
    if nivel_do_titulo(paragrafo) is not None:
        return False

    texto = paragrafo.text.strip()
    if not texto or not parece_citacao_direta(texto):
        return False

    linhas = estimar_linhas(texto, normas.caracteres_por_linha)
    return linhas > normas.max_linhas_citacao_curta


def aplicar_citacoes_longas(documento: DocumentoDocx, normas: NormasABNT) -> int:
    """Aplica o estilo de citação longa e devolve quantas citações tratou."""
    obter_ou_criar_estilo_citacao(documento, normas)

    total = 0
    for paragrafo in documento.paragraphs:
        if eh_citacao_longa(paragrafo, normas):
            _aplicar_citacao(paragrafo, normas)
            total += 1
    return total


def _aplicar_citacao(paragrafo: Paragraph, normas: NormasABNT) -> None:
    """Marca o estilo semântico e garante a formatação de citação longa."""
    paragrafo.style = normas.nome_estilo_citacao

    formato = paragrafo.paragraph_format
    formato.left_indent = Cm(normas.recuo_citacao_cm)
    formato.first_line_indent = Cm(0)
    formato.line_spacing = normas.espacamento_citacao
    formato.space_before = Pt(0)
    formato.space_after = Pt(0)
    formato.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for run in paragrafo.runs:
        definir_fonte(run, normas.fonte_corpo, normas.tamanho_citacao_pt)
