"""Definição de propriedades de fonte em runs do Word."""

from __future__ import annotations

from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.run import Run

# Atributos de fonte que precisam apontar para o mesmo nome.
ATRIBUTOS_FONTE = ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia")


def definir_fonte(run: Run, nome: str, tamanho_pt: int) -> None:
    """Aplica nome e tamanho de fonte a um run, cobrindo todos os alfabetos."""
    run.font.name = nome
    run.font.size = Pt(tamanho_pt)

    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ATRIBUTOS_FONTE:
        rfonts.set(qn(atributo), nome)
