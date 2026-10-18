"""Testes da aplicação de margens (NBR 14724)."""

from __future__ import annotations

import pytest
from docx.document import Document as DocumentoDocx

from formata_abnt.abnt.margens import aplicar_margens
from formata_abnt.abnt.normas import PADRAO


def test_aplica_margens_padrao(documento_exemplo: DocumentoDocx) -> None:
    """As margens seguem 3 cm (sup/esq) e 2 cm (inf/dir)."""
    aplicar_margens(documento_exemplo, PADRAO)
    secao = documento_exemplo.sections[0]

    assert secao.top_margin.cm == pytest.approx(3.0, abs=0.01)
    assert secao.left_margin.cm == pytest.approx(3.0, abs=0.01)
    assert secao.bottom_margin.cm == pytest.approx(2.0, abs=0.01)
    assert secao.right_margin.cm == pytest.approx(2.0, abs=0.01)
