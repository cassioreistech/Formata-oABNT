"""Preferências locais da aplicação, persistidas em JSON."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

NOME_APP = "FormataABNT"


def diretorio_dados() -> Path:
    """Diretório de dados do usuário (``%APPDATA%`` no Windows)."""
    base = os.getenv("APPDATA")
    raiz = Path(base) if base else Path.home() / ".config"
    return raiz / NOME_APP


def caminho_config() -> Path:
    """Caminho do arquivo de configuração JSON."""
    return diretorio_dados() / "config.json"


@dataclass
class Preferencias:
    """Preferências do usuário persistidas entre sessões."""

    fonte: str = "Arial"
    tema: str = "dark"
    ultima_pasta: str | None = None


def carregar_preferencias(caminho: str | Path | None = None) -> Preferencias:
    """Lê as preferências salvas; devolve os padrões se não existirem."""
    destino = Path(caminho) if caminho else caminho_config()
    if not destino.exists():
        return Preferencias()

    try:
        dados = json.loads(destino.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return Preferencias()

    campos = set(Preferencias.__dataclass_fields__)
    validos = {chave: valor for chave, valor in dados.items() if chave in campos}
    return Preferencias(**validos)


def salvar_preferencias(
    preferencias: Preferencias, caminho: str | Path | None = None
) -> Path:
    """Grava as preferências em JSON e devolve o caminho usado."""
    destino = Path(caminho) if caminho else caminho_config()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(asdict(preferencias), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return destino
