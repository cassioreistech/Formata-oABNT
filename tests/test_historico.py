"""Testes do histórico em SQLite."""

from __future__ import annotations

from pathlib import Path

from formata_abnt.historico import inicializar_banco, listar, registrar


def test_registrar_e_listar(tmp_path: Path) -> None:
    """Registros gravados aparecem na listagem, mais recentes primeiro."""
    banco = tmp_path / "historico.db"

    registrar("entrada1.docx", "saida1.docx", caminho=banco)
    registrar("entrada2.docx", "saida2.docx", caminho=banco)

    registros = listar(caminho=banco)

    assert len(registros) == 2
    assert registros[0].arquivo_entrada == "entrada2.docx"
    assert registros[1].arquivo_entrada == "entrada1.docx"


def test_registrar_devolve_id(tmp_path: Path) -> None:
    """O id retornado é crescente."""
    banco = tmp_path / "historico.db"

    primeiro = registrar("a.docx", "a_abnt.docx", caminho=banco)
    segundo = registrar("b.docx", "b_abnt.docx", caminho=banco)

    assert segundo > primeiro


def test_listar_vazio(tmp_path: Path) -> None:
    """Banco novo devolve lista vazia."""
    banco = tmp_path / "historico.db"
    inicializar_banco(banco)

    assert listar(caminho=banco) == []


def test_limite_da_listagem(tmp_path: Path) -> None:
    """O parâmetro limite restringe a quantidade retornada."""
    banco = tmp_path / "historico.db"
    for indice in range(5):
        registrar(f"e{indice}.docx", f"s{indice}.docx", caminho=banco)

    assert len(listar(limite=2, caminho=banco)) == 2
