"""Testes de ponta a ponta da reformatação de um .docx real."""

from __future__ import annotations

import pytest
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.document import Document as DocumentoDocx
from pathlib import Path

from formata_abnt.abnt.reformatador import ReformatadorABNT
from formata_abnt.docx_io import abrir, salvar


def test_reformatar_arquivo_real(arquivo_docx: Path) -> None:
    """Abre um .docx do disco, reformata e grava o resultado."""
    documento = abrir(arquivo_docx)
    ReformatadorABNT().reformatar(documento)
    destino = salvar(documento, arquivo_docx.with_name("saida_abnt.docx"))

    assert destino.exists()


def test_resultado_persiste_apos_reabrir(arquivo_docx: Path, tmp_path: Path) -> None:
    """As regras aplicadas continuam válidas depois de salvar e reabrir."""
    documento = abrir(arquivo_docx)
    ReformatadorABNT().reformatar(documento)
    destino = salvar(documento, tmp_path / "saida_abnt.docx")

    reaberto = abrir(destino)
    secao = reaberto.sections[0]
    assert secao.top_margin.cm == pytest.approx(3.0, abs=0.01)
    assert secao.left_margin.cm == pytest.approx(3.0, abs=0.01)

    corpo = reaberto.paragraphs[1]
    assert corpo.paragraph_format.line_spacing == 1.5
    assert corpo.paragraph_format.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY
    assert corpo.runs[0].font.name == "Times New Roman"


def test_reformatar_documento_vazio() -> None:
    """Não quebra ao reformatar um documento sem parágrafos de texto."""
    from docx import Document

    documento: DocumentoDocx = Document()
    ReformatadorABNT().reformatar(documento)
    assert documento.sections[0].left_margin.cm == pytest.approx(3.0, abs=0.01)
