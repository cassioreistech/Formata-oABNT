"""Testes da formatação de parágrafos de corpo (NBR 14724)."""

from __future__ import annotations

import pytest
from docx.document import Document as DocumentoDocx
from docx.enum.text import WD_ALIGN_PARAGRAPH

from formata_abnt.abnt.normas import PADRAO
from formata_abnt.abnt.paragrafos import aplicar_espacamento_corpo
from formata_abnt.abnt.titulos import nivel_do_titulo


def test_espacamento_recuo_e_justificado(documento_exemplo: DocumentoDocx) -> None:
    """Corpo fica com espaçamento 1,5, justificado e recuo de 1,25 cm."""
    aplicar_espacamento_corpo(documento_exemplo, PADRAO)

    corpo = [
        p
        for p in documento_exemplo.paragraphs
        if p.text and nivel_do_titulo(p) is None
    ]
    assert corpo
    for paragrafo in corpo:
        formato = paragrafo.paragraph_format
        assert formato.line_spacing == 1.5
        assert formato.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY
        assert formato.first_line_indent.cm == pytest.approx(1.25, abs=0.01)


def test_titulos_preservados(documento_exemplo: DocumentoDocx) -> None:
    """O espaçamento de corpo não deve alterar títulos."""
    titulo = documento_exemplo.paragraphs[0]
    alinhamento_original = titulo.paragraph_format.alignment

    aplicar_espacamento_corpo(documento_exemplo, PADRAO)

    assert titulo.paragraph_format.alignment == alinhamento_original
