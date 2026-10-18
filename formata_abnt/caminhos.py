"""Utilidades de caminho de arquivo."""

from __future__ import annotations

from pathlib import Path

SUFIXO_SAIDA = "_abnt"


def nome_saida_padrao(entrada: str | Path) -> Path:
    """Gera o caminho de saída padrão: ``arquivo.docx`` -> ``arquivo_abnt.docx``."""
    caminho = Path(entrada)
    return caminho.with_name(f"{caminho.stem}{SUFIXO_SAIDA}{caminho.suffix}")
