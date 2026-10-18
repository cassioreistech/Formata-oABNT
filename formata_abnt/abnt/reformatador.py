"""Orquestração da reformatação de um .docx segundo as normas ABNT."""

from __future__ import annotations

from docx.document import Document as DocumentoDocx

from formata_abnt.abnt.fontes import aplicar_fonte_corpo, definir_fonte_padrao
from formata_abnt.abnt.margens import aplicar_margens
from formata_abnt.abnt.normas import PADRAO, NormasABNT
from formata_abnt.abnt.paragrafos import aplicar_espacamento_corpo
from formata_abnt.abnt.titulos import aplicar_titulos


class ReformatadorABNT:
    """Aplica as regras de layout da NBR 14724 a um documento .docx."""

    def __init__(self, normas: NormasABNT = PADRAO) -> None:
        self.normas = normas

    def reformatar(self, documento: DocumentoDocx) -> DocumentoDocx:
        """Reformata o documento no lugar e devolve o mesmo objeto."""
        aplicar_margens(documento, self.normas)
        aplicar_espacamento_corpo(documento, self.normas)
        aplicar_fonte_corpo(documento, self.normas)
        aplicar_titulos(documento, self.normas)
        definir_fonte_padrao(documento, self.normas)
        return documento
