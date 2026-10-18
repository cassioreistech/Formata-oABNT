"""Testes da aplicação de papel A4 e margens (NBR 14724)."""

from __future__ import annotations

import pytest
from docx.document import Document as DocumentoDocx

from formata_abnt.margens import aplicar_margens
from formata_abnt.normas import PADRAO


def test_aplica_papel_a4_e_margens(documento_exemplo: DocumentoDocx) -> None:
    """O documento passa a ser A4 com margens 3/2/3/2 cm."""
    aplicar_margens(documento_exemplo, PADRAO)
    secao = documento_exemplo.sections[0]

    assert secao.page_width.cm == pytest.approx(21.0, abs=0.01)
    assert secao.page_height.cm == pytest.approx(29.7, abs=0.01)
    assert secao.top_margin.cm == pytest.approx(3.0, abs=0.01)
    assert secao.left_margin.cm == pytest.approx(3.0, abs=0.01)
    assert secao.bottom_margin.cm == pytest.approx(2.0, abs=0.01)
    assert secao.right_margin.cm == pytest.approx(2.0, abs=0.01)
