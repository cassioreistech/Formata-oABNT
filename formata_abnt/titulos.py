"""Detecção e formatação da hierarquia de títulos (NBR 6024)."""

from __future__ import annotations

import re

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

from formata_abnt.normas import NormasABNT
from formata_abnt.runs import definir_fonte

# Estilos que já indicam título (inglês e português).
_PREFIXOS_TITULO = ("heading ", "título ", "titulo ")

# Numeração progressiva: "1. INTRODUÇÃO", "1.1 Objetivos", "2.3.1 Método".
_NUMERACAO = re.compile(r"^(\d+(?:\.\d+)*)[.)]?\s+\S")

ALINHAMENTO_POR_NIVEL: dict[int, WD_ALIGN_PARAGRAPH] = {
    1: WD_ALIGN_PARAGRAPH.CENTER,
    2: WD_ALIGN_PARAGRAPH.LEFT,
    3: WD_ALIGN_PARAGRAPH.LEFT,
    4: WD_ALIGN_PARAGRAPH.LEFT,
    5: WD_ALIGN_PARAGRAPH.LEFT,
}

ESPACO_ANTES_POR_NIVEL: dict[int, int] = {1: 24, 2: 18, 3: 12, 4: 12, 5: 12}
ESPACO_DEPOIS_POR_NIVEL: dict[int, int] = {1: 12, 2: 12, 3: 6, 4: 6, 5: 6}

_COR_TITULO = RGBColor(0, 0, 0)


def nivel_por_estilo(paragrafo: Paragraph) -> int | None:
    """Devolve o nível quando o parágrafo já usa um estilo de título."""
    nome = (paragrafo.style.name or "").strip().lower()

    if nome in ("title", "título", "titulo"):
        return 1

    for prefixo in _PREFIXOS_TITULO:
        if nome.startswith(prefixo):
            resto = nome[len(prefixo) :].strip()
            if resto.isdigit():
                return int(resto)

    return None


def nivel_por_numeracao(texto: str) -> int | None:
    """Devolve o nível inferido pela numeração do texto, senão None."""
    encontrado = _NUMERACAO.match(texto.strip())
    if not encontrado:
        return None
    return encontrado.group(1).count(".") + 1


def nivel_do_titulo(paragrafo: Paragraph) -> int | None:
    """Devolve o nível do título (1–5) ou None se não for título."""
    return nivel_por_estilo(paragrafo) or nivel_por_numeracao(paragrafo.text)


def aplicar_titulos(documento: DocumentoDocx, normas: NormasABNT) -> int:
    """Formata todos os títulos identificados e devolve a quantidade."""
    total = 0
    for paragrafo in documento.paragraphs:
        nivel = nivel_do_titulo(paragrafo)
        if nivel is None:
            continue
        _aplicar_titulo(documento, paragrafo, nivel, normas)
        total += 1
    return total


def _aplicar_titulo(
    documento: DocumentoDocx, paragrafo: Paragraph, nivel: int, normas: NormasABNT
) -> None:
    """Aplica estilo, alinhamento e fonte a um único título."""
    _definir_estilo_de_titulo(documento, paragrafo, nivel)

    formato = paragrafo.paragraph_format
    formato.alignment = ALINHAMENTO_POR_NIVEL.get(nivel, WD_ALIGN_PARAGRAPH.LEFT)
    formato.first_line_indent = Cm(0)
    formato.line_spacing = normas.espacamento_linhas
    formato.space_before = Pt(ESPACO_ANTES_POR_NIVEL.get(nivel, 12))
    formato.space_after = Pt(ESPACO_DEPOIS_POR_NIVEL.get(nivel, 6))

    for run in paragrafo.runs:
        definir_fonte(run, normas.fonte_titulo, normas.tamanho_titulo_pt)
        run.bold = True
        run.italic = nivel >= 4
        run.underline = False
        run.font.color.rgb = _COR_TITULO


def _definir_estilo_de_titulo(
    documento: DocumentoDocx, paragrafo: Paragraph, nivel: int
) -> None:
    """Associa o estilo Heading correspondente (para sumário/navegação)."""
    nome = f"Heading {min(nivel, 9)}"
    try:
        paragrafo.style = documento.styles[nome]
    except KeyError:
        pass
