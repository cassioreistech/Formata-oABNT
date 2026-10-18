"""Criação e obtenção do estilo de citação longa da ABNT."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.styles.style import ParagraphStyle

from formata_abnt.normas import NormasABNT
from formata_abnt.runs import ATRIBUTOS_FONTE


def obter_ou_criar_estilo_citacao(
    documento: DocumentoDocx, normas: NormasABNT
) -> ParagraphStyle:
    """Devolve o estilo ``ABNT_CitacaoLonga``, criando-o se ainda não existir."""
    nome = normas.nome_estilo_citacao
    estilos = documento.styles

    try:
        return estilos[nome]
    except KeyError:
        pass

    estilo = estilos.add_style(nome, WD_STYLE_TYPE.PARAGRAPH)
    estilo.base_style = estilos["Normal"]

    estilo.font.name = normas.fonte_corpo
    estilo.font.size = Pt(normas.tamanho_citacao_pt)
    rpr = estilo.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ATRIBUTOS_FONTE:
        rfonts.set(qn(atributo), normas.fonte_corpo)

    formato = estilo.paragraph_format
    formato.left_indent = Cm(normas.recuo_citacao_cm)
    formato.first_line_indent = Cm(0)
    formato.line_spacing = normas.espacamento_citacao
    formato.space_before = Pt(0)
    formato.space_after = Pt(0)
    formato.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    return estilo
