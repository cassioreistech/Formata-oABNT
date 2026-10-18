"""Fixtures compartilhadas dos testes."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from docx import Document
from docx.document import Document as DocumentoDocx


@pytest.fixture
def documento_exemplo() -> DocumentoDocx:
    """Documento .docx com título, subtítulo e parágrafos de corpo."""
    doc = Document()
    doc.add_heading("Introdução", level=1)
    doc.add_paragraph("Primeiro parágrafo do trabalho acadêmico usado no teste.")
    doc.add_heading("Justificativa", level=2)
    doc.add_paragraph("Parágrafo que descreve a justificativa da pesquisa.")
    return doc


@pytest.fixture
def arquivo_docx(tmp_path: Path, documento_exemplo: DocumentoDocx) -> Path:
    """Documento .docx gravado em disco, simulando um arquivo real."""
    destino = tmp_path / "entrada.docx"
    documento_exemplo.save(str(destino))
    return destino
