"""Formatação de parágrafos de corpo (NBR 14724)."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

from formata_abnt.abnt.normas import NormasABNT
from formata_abnt.abnt.titulos import nivel_do_titulo


def aplicar_espacamento_corpo(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Define espaçamento 1,5, texto justificado e recuo de 1,25 cm no corpo."""
    for paragrafo in documento.paragraphs:
        if nivel_do_titulo(paragrafo) is not None:
            continue

        formato = paragrafo.paragraph_format
        formato.line_spacing = normas.espacamento_linhas
        formato.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        formato.first_line_indent = Cm(normas.recuo_primeira_linha_cm)
