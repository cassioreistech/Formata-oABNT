"""Modelos de dados do sistema de formatação ABNT.

Define as estruturas de dados que representam um documento acadêmico,
suas seções, referências, citações e metadados.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from src.core.config import TipoDocumento


# ── Autor ───────────────────────────────────────────────────────────────────


class Autor(BaseModel):
    """Autor do documento."""

    nome_completo: str
    nome_citacao: str | None = None  # SOBRENOME, Nome
    afiliacao: str | None = None
    orcid: str | None = None

    @property
    def nome_formatado(self) -> str:
        """Retorna o nome no formato de citação: SOBRENOME, Nome."""
        if self.nome_citacao:
            return self.nome_citacao
        partes = self.nome_completo.strip().split()
        if len(partes) < 2:
            return self.nome_completo.upper()
        sobrenome = partes[-1].upper()
        nome = " ".join(partes[:-1])
        return f"{sobrenome}, {nome}"


# ── Seção ───────────────────────────────────────────────────────────────────


class NivelSecao(int, Enum):
    """Nível hierárquico de uma seção."""

    NIVEL_1 = 1
    NIVEL_2 = 2
    NIVEL_3 = 3
    NIVEL_4 = 4
    NIVEL_5 = 5


class Secao(BaseModel):
    """Seção/capítulo do documento."""

    titulo: str
    nivel: NivelSecao = NivelSecao.NIVEL_1
    numeracao: str | None = None  # Ex: "1", "1.1", "1.1.1"
    conteudo: list[str] = Field(default_factory=list)  # Parágrafos
    subsecoes: list[Secao] = Field(default_factory=list)

    # Metadados opcionais
    epigrafe: str | None = None
    nota_rodape: str | None = None


# ── Citação ─────────────────────────────────────────────────────────────────


class TipoCitacao(str, Enum):
    """Tipos de citação conforme NBR 10520."""

    DIRETA_CURTA = "direta_curta"  # Até 3 linhas, no corpo
    DIRETA_LONGA = "direta_longa"  # Mais de 3 linhas, bloco
    INDIRETA = "indireta"  # Paráfrase
    CITACAO_CITACAO = "citacao_de_citacao"  # Apud


class Citacao(BaseModel):
    """Citação no texto."""

    tipo: TipoCitacao
    texto: str
    autor: str
    ano: int
    pagina: int | None = None
    apud: str | None = None  # Para citação de citação


# ── Referência ──────────────────────────────────────────────────────────────


class TipoReferencia(str, Enum):
    """Tipos de referência mais comuns."""

    LIVRO = "livro"
    ARTIGO_PERIODICO = "artigo_periodico"
    ARTIGO_JORNAL = "artigo_jornal"
    CAPITULO_LIVRO = "capitulo_livro"
    TESE_DISSERTACAO = "tese_dissertacao"
    DOCUMENTO_ELETRONICO = "documento_eletronico"
    SITE = "site"
    VIDEO = "video"
    LEGISLACAO = "legislacao"


class Referencia(BaseModel):
    """Referência bibliográfica conforme NBR 6023."""

    tipo: TipoReferencia
    autores: list[str]
    titulo: str
    # Campos comuns
    ano: int | str
    editora: str | None = None
    edicao: str | None = None
    local: str | None = None
    isbn: str | None = None
    doi: str | None = None
    url: str | None = None
    data_acesso: date | None = None
    # Campos específicos
    subtitulo: str | None = None
    volume: str | None = None
    numero: str | None = None
    paginas: str | None = None  # "p. 10-25"
    revista: str | None = None  # Para artigo de periódico
    instituicao: str | None = None  # Para tese/dissertacao
    grau: str | None = None  # "Doutorado", "Mestrado"
    organizador: str | None = None  # Para capítulo de livro
    # Para citação de citação
    apud_autores: list[str] | None = None
    apud_ano: int | str | None = None


# ── Figura e Tabela ─────────────────────────────────────────────────────────


class Figura(BaseModel):
    """Figura/ilustração no documento."""

    caminho: str  # Caminho do arquivo
    legenda: str
    fonte: str | None = None
    numeracao: str | None = None  # "Figura 1"


class Tabela(BaseModel):
    """Tabela no documento."""

    dados: list[list[str]]
    legenda: str
    fonte: str | None = None
    numeracao: str | None = None  # "Tabela 1"


# ── Metadados do documento ──────────────────────────────────────────────────


class MetadadosDocumento(BaseModel):
    """Metadados gerais do documento."""

    titulo: str
    subtitulo: str | None = None
    autores: list[Autor] = Field(min_length=1)
    tipo: TipoDocumento
    instituicao: str
    curso: str | None = None
    cidade: str
    estado: str | None = None
    ano: int
    # Orientador
    orientador: str | None = None
    coorientador: str | None = None
    # Área de concentração
    area_concentracao: str | None = None
    # Palavras-chave
    palavras_chave: list[str] = Field(default_factory=list)
    # Abstract
    abstract: str | None = None


# ── Documento completo ──────────────────────────────────────────────────────


class Documento(BaseModel):
    """Modelo principal — representa um documento acadêmico completo."""

    metadados: MetadadosDocumento
    # Pré-textuais
    resumo: str | None = None
    abstract: str | None = None
    # Textuais
    secoes: list[Secao] = Field(default_factory=list)
    # Pós-textuais
    referencias: list[Referencia] = Field(default_factory=list)
    figuras: list[Figura] = Field(default_factory=list)
    tabelas: list[Tabela] = Field(default_factory=list)
    # Apêndices e anexos
    apendices: list[Secao] = Field(default_factory=list)
    anexos: list[Secao] = Field(default_factory=list)