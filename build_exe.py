"""Empacotamento do aplicativo em executável único via PyInstaller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

NOME_EXECUTAVEL = "FormataABNT"
ARQUIVO_ENTRADA = "app_gui.py"
PACOTES_COLETADOS = ("customtkinter", "tkinterdnd2", "docx")


def comando_pyinstaller(onefile: bool = True) -> list[str]:
    """Monta o comando do PyInstaller para gerar o executável."""
    comando = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        NOME_EXECUTAVEL,
    ]
    if onefile:
        comando.append("--onefile")
    for pacote in PACOTES_COLETADOS:
        comando.extend(["--collect-all", pacote])
    comando.append(ARQUIVO_ENTRADA)
    return comando


def limpar_artefatos() -> None:
    """Remove pastas e arquivos gerados por builds anteriores."""
    for nome in ("build", "dist"):
        shutil.rmtree(nome, ignore_errors=True)
    for spec in Path(".").glob("*.spec"):
        spec.unlink(missing_ok=True)


def nome_do_executavel() -> str:
    """Nome final do executável conforme o sistema operacional."""
    return f"{NOME_EXECUTAVEL}.exe" if sys.platform.startswith("win") else NOME_EXECUTAVEL


def build(onefile: bool = True) -> Path:
    """Executa o PyInstaller e devolve o caminho do executável gerado."""
    limpar_artefatos()
    subprocess.run(comando_pyinstaller(onefile), check=True)
    return Path("dist") / nome_do_executavel()


def main(argv: list[str] | None = None) -> int:
    """Gera o executável; use ``--onedir`` para pasta em vez de arquivo único."""
    argumentos = sys.argv[1:] if argv is None else argv
    onefile = "--onedir" not in argumentos
    destino = build(onefile=onefile)
    print(f"Executável gerado em: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
