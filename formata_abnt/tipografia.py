"""Aplicação da tipografia ABNT ao corpo do texto."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from formata_abnt.normas import NormasABNT
from formata_abnt.runs import ATRIBUTOS_FONTE, definir_fonte
from formata_abnt.titulos import nivel_do_titulo


def aplicar_tipografia_corpo(documento: DocumentoDocx, normas: NormasABNT) -> int:
    """Normaliza fonte, espaçamento, recuo e justificação dos parágrafos de corpo."""
    total = 0
    for paragrafo in documento.paragraphs:
        if nivel_do_titulo(paragrafo) is not None:
            continue
        if (paragrafo.style.name or "") == normas.nome_estilo_citacao:
            continue

        formato = paragrafo.paragraph_format
        formato.line_spacing = normas.espacamento_linhas
        formato.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        formato.first_line_indent = Cm(normas.recuo_primeira_linha_cm)
        formato.space_before = Pt(0)
        formato.space_after = Pt(0)

        for run in paragrafo.runs:
            definir_fonte(run, normas.fonte_corpo, normas.tamanho_corpo_pt)

        total += 1
    return total


def definir_estilo_normal(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Ajusta o estilo Normal para que novos textos herdem a fonte ABNT."""
    estilo = documento.styles["Normal"]
    estilo.font.name = normas.fonte_corpo
    estilo.font.size = Pt(normas.tamanho_corpo_pt)

    rpr = estilo.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ATRIBUTOS_FONTE:
        rfonts.set(qn(atributo), normas.fonte_corpo)
