"""Aplicação de fonte e tamanho a runs, preservando marcações de texto."""

from __future__ import annotations

from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.run import Run

# Atributos de fonte que precisam apontar para o mesmo nome.
ATRIBUTOS_FONTE = ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia")


def definir_fonte(run: Run, nome: str, tamanho_pt: int) -> None:
    """Define apenas nome e tamanho da fonte.

    Negrito, itálico e sublinhado do run são preservados; textos vazios
    são ignorados para não criar formatação órfã.
    """
    if not run.text:
        return

    run.font.name = nome
    run.font.size = Pt(tamanho_pt)

    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ATRIBUTOS_FONTE:
        rfonts.set(qn(atributo), nome)
