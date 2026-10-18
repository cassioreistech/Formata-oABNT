"""Testes da formatação de títulos (NBR 6024 / 14724)."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH

from formata_abnt.abnt.normas import PADRAO
from formata_abnt.abnt.titulos import aplicar_titulos, nivel_do_titulo


def test_detecta_nivel_de_titulo(documento_exemplo: DocumentoDocx) -> None:
    """Reconhece títulos pelos estilos Heading 1 e Heading 2."""
    niveis = [nivel_do_titulo(p) for p in documento_exemplo.paragraphs]
    assert 1 in niveis
    assert 2 in niveis


def test_titulo_nivel_1_centralizado_e_negrito(documento_exemplo: DocumentoDocx) -> None:
    """Título de nível 1 fica centralizado, negrito e sem recuo."""
    aplicar_titulos(documento_exemplo, PADRAO)

    titulo = documento_exemplo.paragraphs[0]
    assert nivel_do_titulo(titulo) == 1
    assert titulo.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert titulo.paragraph_format.first_line_indent.cm == 0
    assert titulo.runs
    assert all(run.bold for run in titulo.runs)


def test_titulo_nivel_2_alinhado_a_esquerda(documento_exemplo: DocumentoDocx) -> None:
    """Título de nível 2 fica alinhado à esquerda."""
    aplicar_titulos(documento_exemplo, PADRAO)

    titulo = documento_exemplo.paragraphs[2]
    assert nivel_do_titulo(titulo) == 2
    assert titulo.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.LEFT


def test_paragrafo_comum_nao_e_titulo(documento_exemplo: DocumentoDocx) -> None:
    """Parágrafo de corpo não é identificado como título."""
    assert nivel_do_titulo(documento_exemplo.paragraphs[1]) is None
