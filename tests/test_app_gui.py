"""Testes leves da camada gráfica (sem abrir janela)."""

from __future__ import annotations

from pathlib import Path

import app_gui


def test_modulo_importa_sem_erros() -> None:
    """O módulo da GUI importa sem depender de display."""
    assert hasattr(app_gui, "AplicacaoABNT")
    assert hasattr(app_gui, "main")


def test_nome_sugerido() -> None:
    """O nome sugerido de saída adiciona o sufixo _abnt."""
    assert app_gui.nome_sugerido(Path("tcc.docx")).name == "tcc_abnt.docx"


def test_abrir_pasta_e_chamavel() -> None:
    """A função de abrir pasta existe e é chamável."""
    assert callable(app_gui.abrir_pasta)
