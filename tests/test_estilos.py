"""Testes do estilo de citação longa."""

from __future__ import annotations

import pytest
from docx.document import Document as DocumentoDocx

from formata_abnt.estilos import obter_ou_criar_estilo_citacao
from formata_abnt.normas import PADRAO


def test_cria_estilo_citacao_longa(documento_exemplo: DocumentoDocx) -> None:
    """Cria o estilo com recuo de 4 cm, fonte 10 pt e espaçamento simples."""
    estilo = obter_ou_criar_estilo_citacao(documento_exemplo, PADRAO)

    assert estilo.name == PADRAO.nome_estilo_citacao
    assert estilo.paragraph_format.left_indent.cm == pytest.approx(4.0, abs=0.01)
    assert estilo.paragraph_format.line_spacing == 1.0
    assert estilo.font.size.pt == 10


def test_reutiliza_estilo_existente(documento_exemplo: DocumentoDocx) -> None:
    """Chamar duas vezes não recria o estilo."""
    primeiro = obter_ou_criar_estilo_citacao(documento_exemplo, PADRAO)
    segundo = obter_ou_criar_estilo_citacao(documento_exemplo, PADRAO)

    assert primeiro.style_id == segundo.style_id
