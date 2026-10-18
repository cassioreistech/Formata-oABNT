"""Identificação e formatação de títulos (NBR 6024 / NBR 14724)."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

from formata_abnt.abnt.normas import NormasABNT
from formata_abnt.abnt.runs import definir_fonte

# Prefixos de estilo que indicam título, em inglês e português.
_PREFIXOS_TITULO = ("heading ", "título ", "titulo ")

ALINHAMENTO_POR_NIVEL: dict[int, WD_ALIGN_PARAGRAPH] = {
    1: WD_ALIGN_PARAGRAPH.CENTER,
    2: WD_ALIGN_PARAGRAPH.LEFT,
    3: WD_ALIGN_PARAGRAPH.LEFT,
    4: WD_ALIGN_PARAGRAPH.LEFT,
    5: WD_ALIGN_PARAGRAPH.LEFT,
}

ESPACO_ANTES_POR_NIVEL: dict[int, int] = {1: 24, 2: 18, 3: 12, 4: 12, 5: 12}
ESPACO_DEPOIS_POR_NIVEL: dict[int, int] = {1: 12, 2: 12, 3: 6, 4: 6, 5: 6}


def nivel_do_titulo(paragrafo: Paragraph) -> int | None:
    """Devolve o nível (1–5) se o parágrafo for um título, senão None."""
    nome = (paragrafo.style.name or "").strip().lower()

    if nome in ("title", "título", "titulo"):
        return 1

    for prefixo in _PREFIXOS_TITULO:
        if nome.startswith(prefixo):
            resto = nome[len(prefixo) :].strip()
            if resto.isdigit():
                return int(resto)

    return None


def aplicar_titulos(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Formata todos os títulos do documento conforme o nível hierárquico."""
    for paragrafo in documento.paragraphs:
        nivel = nivel_do_titulo(paragrafo)
        if nivel is not None:
            _aplicar_titulo(paragrafo, nivel, normas)


def _aplicar_titulo(paragrafo: Paragraph, nivel: int, normas: NormasABNT) -> None:
    """Aplica alinhamento, espaçamento e fonte a um único título."""
    formato = paragrafo.paragraph_format
    formato.alignment = ALINHAMENTO_POR_NIVEL.get(nivel, WD_ALIGN_PARAGRAPH.LEFT)
    formato.line_spacing = normas.espacamento_linhas
    formato.first_line_indent = Cm(0)
    formato.space_before = Pt(ESPACO_ANTES_POR_NIVEL.get(nivel, 12))
    formato.space_after = Pt(ESPACO_DEPOIS_POR_NIVEL.get(nivel, 6))

    for run in paragrafo.runs:
        definir_fonte(run, normas.fonte_titulo, normas.tamanho_titulo_pt)
        run.bold = True
        run.italic = nivel >= 4
