"""Testes das preferências locais (JSON)."""

from __future__ import annotations

from pathlib import Path

from formata_abnt.config import (
    ConfiguracaoPOP,
    Preferencias,
    carregar_preferencias,
    diretorio_dados,
    salvar_preferencias,
)


def test_salvar_e_carregar(tmp_path: Path) -> None:
    """As preferências gravadas são recuperadas iguais."""
    arquivo = tmp_path / "config.json"
    original = Preferencias(
        fonte="Times New Roman",
        tema="light",
        ultima_pasta="C:/docs",
        pop=ConfiguracaoPOP(ativo=True, nome_empresa="X", titulo_pop="Y"),
    )

    salvar_preferencias(original, arquivo)
    recuperado = carregar_preferencias(arquivo)

    assert recuperado == original


def test_carrega_padroes_quando_ausente(tmp_path: Path) -> None:
    """Sem arquivo, devolve os valores padrão."""
    caminho = tmp_path / "inexistente.json"

    assert carregar_preferencias(caminho) == Preferencias()


def test_ignora_campos_desconhecidos(tmp_path: Path) -> None:
    """Campos extras no JSON não quebram a leitura."""
    arquivo = tmp_path / "config.json"
    arquivo.write_text('{"fonte": "Arial", "desconhecido": 1}', encoding="utf-8")

    assert carregar_preferencias(arquivo).fonte == "Arial"


def test_pop_persiste_como_objeto_aninhado(tmp_path: Path) -> None:
    """A configuração POP é salva e carregada como dataclass aninhada."""
    arquivo = tmp_path / "config.json"
    original = Preferencias(pop=ConfiguracaoPOP(ativo=True, nome_empresa="Empresa"))

    salvar_preferencias(original, arquivo)
    recuperado = carregar_preferencias(arquivo)

    assert recuperado.pop == original.pop
    assert recuperado.pop.ativo is True
    assert recuperado.pop.nome_empresa == "Empresa"


def test_diretorio_dados_usa_appdata(tmp_path: Path, monkeypatch) -> None:
    """O diretório de dados respeita a variável APPDATA."""
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert diretorio_dados() == tmp_path / "FormataABNT"
