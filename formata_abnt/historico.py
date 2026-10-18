"""Histórico de formatações, persistido em SQLite local."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from formata_abnt.config import diretorio_dados

_SCHEMA = """
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo_entrada TEXT NOT NULL,
    arquivo_saida TEXT NOT NULL,
    status TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
"""


@dataclass
class RegistroHistorico:
    """Uma execução de formatação registrada no histórico."""

    id: int
    arquivo_entrada: str
    arquivo_saida: str
    status: str
    criado_em: str


def caminho_banco() -> Path:
    """Caminho do banco SQLite do histórico."""
    return diretorio_dados() / "historico.db"


def inicializar_banco(caminho: str | Path | None = None) -> Path:
    """Garante a existência do banco e da tabela de histórico."""
    destino = Path(caminho) if caminho else caminho_banco()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(destino)) as conexao:
        conexao.execute(_SCHEMA)
        conexao.commit()
    return destino


def registrar(
    arquivo_entrada: str | Path,
    arquivo_saida: str | Path,
    status: str = "concluido",
    caminho: str | Path | None = None,
) -> int:
    """Registra uma formatação no histórico e devolve o id gerado."""
    destino = inicializar_banco(caminho)
    with closing(sqlite3.connect(destino)) as conexao:
        cursor = conexao.execute(
            "INSERT INTO historico "
            "(arquivo_entrada, arquivo_saida, status, criado_em) "
            "VALUES (?, ?, ?, ?)",
            (
                str(arquivo_entrada),
                str(arquivo_saida),
                status,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conexao.commit()
        return int(cursor.lastrowid or 0)


def listar(limite: int = 50, caminho: str | Path | None = None) -> list[RegistroHistorico]:
    """Lista os registros mais recentes do histórico."""
    destino = inicializar_banco(caminho)
    with closing(sqlite3.connect(destino)) as conexao:
        conexao.row_factory = sqlite3.Row
        linhas = conexao.execute(
            "SELECT id, arquivo_entrada, arquivo_saida, status, criado_em "
            "FROM historico ORDER BY id DESC LIMIT ?",
            (limite,),
        ).fetchall()
    return [RegistroHistorico(**dict(linha)) for linha in linhas]
