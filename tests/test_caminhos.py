"""Testes das utilidades de caminho."""

from __future__ import annotations

from pathlib import Path

from formata_abnt.caminhos import nome_saida_padrao


def test_nome_saida_padrao() -> None:
    """O sufixo ``_abnt`` é inserido antes da extensão."""
    assert nome_saida_padrao("tcc.docx") == Path("tcc_abnt.docx")


def test_nome_saida_padrao_com_caminho() -> None:
    """Funciona com caminhos completos e outros nomes."""
    resultado = nome_saida_padrao(Path("C:/docs/monografia final.docx"))
    assert resultado.name == "monografia final_abnt.docx"
