"""Aplicação de papel A4 e margens ABNT (NBR 14724)."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.shared import Cm

from formata_abnt.normas import NormasABNT


def aplicar_margens(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Define papel A4 e as margens ABNT em todas as seções."""
    for secao in documento.sections:
        secao.page_width = Cm(normas.largura_papel_cm)
        secao.page_height = Cm(normas.altura_papel_cm)
        secao.top_margin = Cm(normas.margem_superior_cm)
        secao.bottom_margin = Cm(normas.margem_inferior_cm)
        secao.left_margin = Cm(normas.margem_esquerda_cm)
        secao.right_margin = Cm(normas.margem_direita_cm)
