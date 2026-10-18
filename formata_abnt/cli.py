"""Interface de linha de comando: reformata um .docx segundo a ABNT."""

from __future__ import annotations

import argparse
from pathlib import Path

from formata_abnt.abnt.normas import NormasABNT
from formata_abnt.abnt.reformatador import ReformatadorABNT
from formata_abnt.docx_io import abrir, salvar


def main(argv: list[str] | None = None) -> int:
    """Reformata um arquivo .docx existente e grava o resultado."""
    parser = argparse.ArgumentParser(
        prog="formata-abnt",
        description="Reformata um arquivo .docx segundo a NBR 14724.",
    )
    parser.add_argument("entrada", type=Path, help="Arquivo .docx de entrada")
    parser.add_argument(
        "-o",
        "--saida",
        type=Path,
        default=None,
        help="Arquivo .docx de saída (padrão: <entrada>_abnt.docx)",
    )
    parser.add_argument(
        "--fonte",
        default="Times New Roman",
        help="Fonte do texto (padrão: Times New Roman)",
    )
    args = parser.parse_args(argv)

    saida = args.saida or args.entrada.with_name(f"{args.entrada.stem}_abnt.docx")
    normas = NormasABNT(fonte_corpo=args.fonte, fonte_titulo=args.fonte)

    documento = abrir(args.entrada)
    ReformatadorABNT(normas).reformatar(documento)
    salvar(documento, saida)

    print(f"Documento reformatado: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
