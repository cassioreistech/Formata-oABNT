"""Configurações e constantes ABNT.

Referências:
- NBR 14724:2024 — Informação e documentação — Trabalhos acadêmicos
- NBR 6023:2018 — Informação e documentação — Referências
- NBR 6024:2012 — Informação e documentação — Numeração progressiva
- NBR 6027:2012 — Informação e documentação — Sumário
- NBR 6028:2021 — Informação e documentação — Resumo
- NBR 10520:2023 — Informação e documentação — Citações
"""

from __future__ import annotations

from enum import Enum


# ── Tipos de documento ──────────────────────────────────────────────────────


class TipoDocumento(str, Enum):
    """Tipos de documento acadêmico suportados."""

    TCC = "tcc"
    ARTIGO = "artigo"
    DISSERTACAO = "dissertacao"
    TESE = "tese"
    RELATORIO = "relatorio"
    PROJETO_PESQUISA = "projeto_pesquisa"


# ── Constantes de formatação (NBR 14724) ────────────────────────────────────


class Formatacao:
    """Constantes de formatação ABNT."""

    # Margens (cm)
    MARGEM_SUPERIOR = 3.0
    MARGEM_INFERIOR = 2.0
    MARGEM_ESQUERDA = 3.0
    MARGEM_DIREITA = 2.0

    # Fonte
    FONTE_PADRAO = "Times New Roman"
    FONTE_ALTERNATIVA = "Arial"
    TAMANHO_FONTE = 12  # pt
    TAMANHO_FONTE_NOTAS = 10  # pt

    # Espaçamento
    ESPACAMENTO_LINHAS = 1.5
    ESPACAMENTO_SIMPLES = 1.0
    ESPACAMENTO_TITULO_ANTES = 0  # pt (antes do parágrafo)
    ESPACAMENTO_TITULO_DEPOIS = 12  # pt (depois do parágrafo)

    # Parágrafo
    INDENTACAO_PRIMEIRA_LINHA = 1.25  # cm

    # Numeração de páginas
    PAGINA_INICIAL_ELEMENTOS_TEXTUAIS = 1


# ── Hierarquia de títulos ───────────────────────────────────────────────────


class NivelTitulo:
    """Níveis de título conforme NBR 6024."""

    NIVEL_1 = 1  # CENTRALIZADO, MAIÚSCULO, NEGRITO
    NIVEL_2 = 2  # À ESQUERDA, MAIÚSCULO, NEGRITO
    NIVEL_3 = 3  # À ESQUERDA, Iniciais em Maiúsculo, NEGRITO
    NIVEL_4 = 4  # À ESQUERDA, Iniciais em Maiúsculo, itálico, negrito
    NIVEL_5 = 5  # À ESQUERDA, Iniciais em Maiúsculo, itálico


# ── Elementos do documento ──────────────────────────────────────────────────


class ElementosPreTextuais:
    """Elementos pré-textuais obrigatórios/opcionais."""

    OBRIGATORIOS = [
        "capa",
        "folha_de_rosto",
        "sumario",
    ]
    OPCIONAIS = [
        "folha_de_aprovacao",
        "dedicatoria",
        "agradecimentos",
        "epigrafe",
        "resumo",
        "lista_ilustracoes",
        "lista_tabelas",
        "lista_abreviaturas",
        "lista_simbolos",
    ]


class ElementosTextuais:
    """Elementos textuais."""

    OBRIGATORIOS = [
        "introducao",
        "desenvolvimento",
        "conclusao",
    ]


class ElementosPosTextuais:
    """Elementos pós-textuais."""

    OBRIGATORIOS = [
        "referencias",
    ]
    OPCIONAIS = [
        "glossario",
        "apendice",
        "anexo",
        "indice",
    ]


# ── Elementos por tipo de documento ─────────────────────────────────────────

ESTRUTURA_DOCUMENTO: dict[TipoDocumento, dict[str, list[str]]] = {
    TipoDocumento.TCC: {
        "pre_textuais": [
            "capa",
            "folha_de_rosto",
            "folha_de_aprovacao",
            "dedicatoria",
            "agradecimentos",
            "epigrafe",
            "resumo",
            "abstract",
            "lista_ilustracoes",
            "lista_tabelas",
            "lista_abreviaturas",
            "lista_simbolos",
            "sumario",
        ],
        "textuais": [
            "introducao",
            "desenvolvimento",
            "conclusao",
        ],
        "pos_textuais": [
            "referencias",
            "glossario",
            "apendice",
            "anexo",
            "indice",
        ],
    },
    TipoDocumento.ARTIGO: {
        "pre_textuais": [
            "titulo",
            "autores",
            "resumo",
            "abstract",
            "palavras_chave",
        ],
        "textuais": [
            "introducao",
            "desenvolvimento",
            "conclusao",
        ],
        "pos_textuais": [
            "referencias",
        ],
    },
    TipoDocumento.DISSERTACAO: {
        "pre_textuais": [
            "capa",
            "folha_de_rosto",
            "folha_de_aprovacao",
            "resumo",
            "abstract",
            "lista_ilustracoes",
            "lista_tabelas",
            "lista_abreviaturas",
            "lista_simbolos",
            "sumario",
        ],
        "textuais": [
            "introducao",
            "desenvolvimento",
            "conclusao",
        ],
        "pos_textuais": [
            "referencias",
            "glossario",
            "apendice",
            "anexo",
            "indice",
        ],
    },
    TipoDocumento.TESE: {
        "pre_textuais": [
            "capa",
            "folha_de_rosto",
            "folha_de_aprovacao",
            "resumo",
            "abstract",
            "lista_ilustracoes",
            "lista_tabelas",
            "lista_abreviaturas",
            "lista_simbolos",
            "sumario",
        ],
        "textuais": [
            "introducao",
            "desenvolvimento",
            "conclusao",
        ],
        "pos_textuais": [
            "referencias",
            "glossario",
            "apendice",
            "anexo",
            "indice",
        ],
    },
    TipoDocumento.RELATORIO: {
        "pre_textuais": [
            "capa",
            "folha_de_rosto",
            "resumo",
            "sumario",
        ],
        "textuais": [
            "introducao",
            "desenvolvimento",
            "conclusao",
        ],
        "pos_textuais": [
            "referencias",
        ],
    },
    TipoDocumento.PROJETO_PESQUISA: {
        "pre_textuais": [
            "capa",
            "folha_de_rosto",
            "sumario",
        ],
        "textuais": [
            "introducao",
            "justificativa",
            "objetivos",
            "metodologia",
            "cronograma",
            "referencias",
        ],
        "pos_textuais": [],
    },
}


# ── Citação (NBR 10520) ─────────────────────────────────────────────────────


class Citacao:
    """Configurações de citação conforme NBR 10520."""

    # Citação curta: até 3 linhas, no corpo do texto, entre aspas
    MAX_LINHAS_CURTA = 3

    # Citação longa: mais de 3 linhas, bloco destacado, recuo 4cm
    INDENTACAO_LONGA = 4.0  # cm da margem esquerda
    TAMANHO_FONTE_LONGA = 10  # pt
    ESPACAMENTO_LONGA = 1.0  # simples


# ── Referências (NBR 6023) ──────────────────────────────────────────────────


class Referencias:
    """Configurações de referências conforme NBR 6023."""

    # Elementos obrigatórios de uma referência:
    # Autor(es). Título. [S.l.]: Editora, ano.
    SEPARADOR_CAMPOS = ". "
    INDENTACAO_FRANCESA = True  # Hanging indent
    ESPACAMENTO_ENTRE = 0  # espaço simples entre referências