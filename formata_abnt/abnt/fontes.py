"""Aplicação de fonte e tamanho ao corpo do texto."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.oxml.ns import qn
from docx.shared import Pt

from formata_abnt.abnt.normas import NormasABNT
from formata_abnt.abnt.runs import ATRIBUTOS_FONTE, definir_fonte
from formata_abnt.abnt.titulos import nivel_do_titulo


def aplicar_fonte_corpo(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Aplica a fonte padronizada aos runs dos parágrafos de corpo."""
    for paragrafo in documento.paragraphs:
        if nivel_do_titulo(paragrafo) is not None:
            continue
        for run in paragrafo.runs:
            definir_fonte(run, normas.fonte_corpo, normas.tamanho_corpo_pt)


def definir_fonte_padrao(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Ajusta o estilo Normal para que textos novos herdem a fonte ABNT."""
    estilo = documento.styles["Normal"]
    estilo.font.name = normas.fonte_corpo
    estilo.font.size = Pt(normas.tamanho_corpo_pt)

    rpr = estilo.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ATRIBUTOS_FONTE:
        rfonts.set(qn(atributo), normas.fonte_corpo)
