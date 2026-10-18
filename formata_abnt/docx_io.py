"""Leitura e escrita de arquivos .docx."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.document import Document as DocumentoDocx


def abrir(caminho: str | Path) -> DocumentoDocx:
    """Abre um arquivo .docx existente."""
    return Document(str(caminho))


def salvar(documento: DocumentoDocx, caminho: str | Path) -> Path:
    """Salva o documento em .docx e devolve o caminho final."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    documento.save(str(destino))
    return destino
