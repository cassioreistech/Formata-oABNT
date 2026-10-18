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


def test_campos_do_formulario_por_tipo() -> None:
    """Cada tipo de referência tem seus campos de formulário definidos."""
    assert set(app_gui.CAMPOS_POR_TIPO) == {"Livro", "Artigo", "Site", "Texto bruto"}
    assert ("url", "URL") in app_gui.CAMPOS_POR_TIPO["Site"]
    assert ("bruto", "Cole aqui o texto da referência") in app_gui.CAMPOS_POR_TIPO[
        "Texto bruto"
    ]


def test_metodos_da_aba_de_referencias_existem() -> None:
    """A classe expõe as ações da aba Gerador de Referências."""
    for metodo in (
        "_montar_aba_referencias",
        "_gerar_referencia",
        "_gerar_e_copiar",
        "_inserir_no_word",
        "_ordenar_docx",
    ):
        assert callable(getattr(app_gui.AplicacaoABNT, metodo))
