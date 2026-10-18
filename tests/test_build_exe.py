"""Testes da configuração de empacotamento com PyInstaller."""

from __future__ import annotations

from build_exe import NOME_EXECUTAVEL, comando_pyinstaller, nome_do_executavel


def test_comando_inclui_pyinstaller() -> None:
    """O comando chama o PyInstaller com o arquivo de entrada correto."""
    comando = comando_pyinstaller()

    assert "-m" in comando
    assert "PyInstaller" in comando
    assert comando[-1] == "app_gui.py"


def test_comando_um_arquivo_unico() -> None:
    """Com onefile=True, --onefile está presente; senão, ausente."""
    assert "--onefile" in comando_pyinstaller(onefile=True)
    assert "--onefile" not in comando_pyinstaller(onefile=False)


def test_comando_coleta_pacotes_de_dados() -> None:
    """Os pacotes com dados (temas do CustomTkinter) são coletados."""
    comando = comando_pyinstaller()

    assert "--collect-all" in comando
    for pacote in ("customtkinter", "tkinterdnd2", "docx"):
        assert pacote in comando


def test_nome_do_executavel() -> None:
    """O nome do executável segue a convenção do sistema."""
    assert NOME_EXECUTAVEL in nome_do_executavel()
