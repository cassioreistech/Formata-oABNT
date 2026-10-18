"""Aplicação das margens da NBR 14724."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx
from docx.shared import Cm

from formata_abnt.abnt.normas import NormasABNT


def aplicar_margens(documento: DocumentoDocx, normas: NormasABNT) -> None:
    """Ajusta as margens de todas as seções do documento."""
    for secao in documento.sections:
        secao.top_margin = Cm(normas.margem_superior_cm)
        secao.bottom_margin = Cm(normas.margem_inferior_cm)
        secao.left_margin = Cm(normas.margem_esquerda_cm)
        secao.right_margin = Cm(normas.margem_direita_cm)
