"""Formatação de referências conforme a ABNT NBR 6023.

Trata os três tipos mais comuns de fontes acadêmicas: livro, artigo de
periódico e site/página web. Cada referência é montada como uma lista de
*segmentos* (texto + indicação de negrito), o que permite aplicar
corretamente o destaque tipográfico ao gravar em arquivos .docx.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

# Abreviações de mês usadas no "Acesso em:" (NBR 6023).
MESES_ABNT = {
    1: "jan.",
    2: "fev.",
    3: "mar.",
    4: "abr.",
    5: "mai.",
    6: "jun.",
    7: "jul.",
    8: "ago.",
    9: "set.",
    10: "out.",
    11: "nov.",
    12: "dez.",
}

TIPOS_VALIDOS = ("livro", "artigo", "site", "generico")

_URL_RE = re.compile(r"(https?://[^\s<>\"']+)")
_ANO_RE = re.compile(r"\b((?:19|20)\d{2})\b")
_VOLUME_RE = re.compile(r"\bv\.\s*(\d+)", re.IGNORECASE)
_NUMERO_RE = re.compile(r"\bn\.\s*(\d+)", re.IGNORECASE)
_PAGINAS_RE = re.compile(r"\bp\.\s*([\d\-\u2013]+)", re.IGNORECASE)
_EDICAO_RE = re.compile(r"\b(\d+)\s*\.?\s*ed\.?", re.IGNORECASE)
_IMPRENTA_RE = re.compile(r"([^.:;]+?):\s*([^:,;]+),\s*((?:19|20)\d{2})")


def normalizar_para_ordenacao(texto: str) -> str:
    """Prepara o texto para ordenação alfabética (sem acentos, minúsculo)."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento).strip().casefold()


@dataclass(frozen=True)
class Segmento:
    """Trecho de uma referência, com indicação de destaque em negrito."""

    texto: str
    negrito: bool = False


@dataclass
class Referencia:
    """Referência formatada, composta por segmentos de texto."""

    segmentos: list[Segmento] = field(default_factory=list)
    tipo: str = "generico"

    @classmethod
    def de_markdown(cls, texto: str, tipo: str = "generico") -> Referencia:
        """Cria a referência a partir de um texto com destaques em ``**``."""
        segmentos = [
            Segmento(parte, negrito=indice % 2 == 1)
            for indice, parte in enumerate(re.split(r"\*\*", texto))
            if parte
        ]
        return cls(segmentos=segmentos, tipo=tipo)

    @property
    def texto_puro(self) -> str:
        """Referência sem marcadores, pronta para copiar como texto simples."""
        return "".join(segmento.texto for segmento in self.segmentos)

    @property
    def texto_markdown(self) -> str:
        """Referência com os destaques sinalizados por ``**``."""
        return "".join(
            f"**{segmento.texto}**" if segmento.negrito else segmento.texto
            for segmento in self.segmentos
        )

    def chave_ordenacao(self) -> str:
        """Chave de ordenação alfabética exigida pela ABNT."""
        return normalizar_para_ordenacao(self.texto_puro)

    def __str__(self) -> str:  # pragma: no cover - conveniência de uso
        return self.texto_markdown


class ABNTReferenceFormatter:
    """Analisa e formata referências bibliográficas (ABNT NBR 6023)."""

    MESES_ABNT = MESES_ABNT

    # ── Utilitários ─────────────────────────────────────────────────────────

    @staticmethod
    def format_author_name(author_full_name: str) -> str:
        """Converte 'João da Silva' em 'SILVA, João da'.

        Também aceita um autor já invertido ('SILVA, João da'), apenas
        garantindo o sobrenome em caixa alta.
        """
        texto = " ".join((author_full_name or "").strip().split())
        if not texto:
            return ""

        if "," in texto:
            sobrenome, _, nome = texto.partition(",")
            sobrenome = sobrenome.strip().upper()
            nome = nome.strip()
            return f"{sobrenome}, {nome}" if nome else sobrenome

        nomes = texto.split()
        if len(nomes) == 1:
            return nomes[0].upper()
        return f"{nomes[-1].upper()}, {' '.join(nomes[:-1])}"

    @staticmethod
    def _data_acesso_formatada(data: datetime | None) -> str:
        """Formata a data como '10 jan. 2026'."""
        referencia_data = data or datetime.now()
        return (
            f"{referencia_data.day} "
            f"{MESES_ABNT[referencia_data.month]} "
            f"{referencia_data.year}"
        )

    @staticmethod
    def _segmento_autor(author: str) -> list[Segmento]:
        """Monta o trecho inicial com o autor, quando existir."""
        autor = ABNTReferenceFormatter.format_author_name(author)
        return [Segmento(f"{autor}. ")] if autor else []

    # ── Formatadores por tipo ───────────────────────────────────────────────

    def format_website(
        self,
        author: str = "",
        title: str = "",
        url: str = "",
        access_date: datetime | None = None,
    ) -> Referencia:
        """Formata referência de site/página web."""
        segmentos = self._segmento_autor(author)
        titulo = (title or "").strip().rstrip(".")

        if titulo:
            if not segmentos:
                # Sem autor, a primeira palavra do título fica em caixa alta e negrito.
                palavras = titulo.split()
                segmentos.append(Segmento(palavras[0].upper(), negrito=True))
                resto = " ".join(palavras[1:])
                segmentos.append(Segmento(f" {resto}" if resto else ""))
                segmentos.append(Segmento(". "))
            else:
                segmentos.append(Segmento(f"{titulo}. "))

        if url:
            segmentos.append(Segmento(f"Disponível em: <{url.strip()}>. "))
        segmentos.append(Segmento(f"Acesso em: {self._data_acesso_formatada(access_date)}."))
        return Referencia(segmentos, tipo="site")

    def format_book(
        self,
        author: str = "",
        title: str = "",
        edition: str = "",
        city: str = "",
        publisher: str = "",
        year: int | str | None = None,
    ) -> Referencia:
        """Formata referência de livro impresso ou digital."""
        segmentos = self._segmento_autor(author)

        titulo = (title or "").strip().rstrip(".")
        if titulo:
            segmentos.append(Segmento(titulo, negrito=True))
            segmentos.append(Segmento(". "))

        edicao = str(edition or "").strip()
        if edicao:
            segmentos.append(Segmento(f"{edicao} ed. "))

        imprenta = ""
        if (city or "").strip():
            imprenta += f"{city.strip()}: "
        if (publisher or "").strip():
            imprenta += publisher.strip()
        if year:
            imprenta += (", " if imprenta else "") + str(year)
        if imprenta:
            segmentos.append(Segmento(f"{imprenta.rstrip(', ')}."))

        return Referencia(segmentos, tipo="livro")

    def format_journal_article(
        self,
        author: str = "",
        article_title: str = "",
        journal_title: str = "",
        city: str = "",
        volume: str = "",
        number: str = "",
        pages: str = "",
        year: int | str | None = None,
    ) -> Referencia:
        """Formata referência de artigo em revista/periódico acadêmico."""
        segmentos = self._segmento_autor(author)

        titulo = (article_title or "").strip().rstrip(".")
        if titulo:
            segmentos.append(Segmento(f"{titulo}. "))

        periodico = (journal_title or "").strip().rstrip(".")
        if periodico:
            # No artigo, o destaque em negrito vai para o título do periódico.
            segmentos.append(Segmento(periodico, negrito=True))

        detalhes: list[str] = []
        if (city or "").strip():
            detalhes.append(city.strip())
        if str(volume or "").strip():
            detalhes.append(f"v. {str(volume).strip()}")
        if str(number or "").strip():
            detalhes.append(f"n. {str(number).strip()}")
        if str(pages or "").strip():
            detalhes.append(f"p. {str(pages).strip()}")
        if year:
            detalhes.append(str(year))

        if detalhes:
            segmentos.append(Segmento(f", {', '.join(detalhes)}."))
        elif periodico:
            segmentos.append(Segmento("."))

        return Referencia(segmentos, tipo="artigo")

    # ── Análise de texto bruto ──────────────────────────────────────────────

    def analisar_texto_bruto(self, texto: str) -> Referencia:
        """Interpreta uma referência já escrita e a reformata segundo a ABNT.

        A leitura é heurística: procura URL (site), indicadores de periódico
        (``v.``, ``n.``, ``p.``) e imprenta ``Cidade: Editora, ano`` (livro).
        Sem correspondência, devolve o texto original como referência genérica.
        """
        limpo = re.sub(r"\s+", " ", (texto or "")).strip()
        if not limpo:
            return Referencia([], tipo="generico")

        if _URL_RE.search(limpo):
            return self._analisar_site(limpo)
        if _VOLUME_RE.search(limpo) or _NUMERO_RE.search(limpo) or _PAGINAS_RE.search(limpo):
            return self._analisar_artigo(limpo)
        if _IMPRENTA_RE.search(limpo):
            return self._analisar_livro(limpo)
        return Referencia([Segmento(limpo)], tipo="generico")

    @staticmethod
    def _separar_autor(texto: str) -> tuple[str, str]:
        """Separa 'AUTOR. Resto...' em autor e restante do texto."""
        encontrado = re.match(r"^([^.]{2,120}?)\.\s+(.*)$", texto)
        if not encontrado:
            return "", texto
        return encontrado.group(1).strip(), encontrado.group(2).strip()

    def _analisar_site(self, texto: str) -> Referencia:
        """Extrai autor, título e URL de um texto de referência de site."""
        encontrado = _URL_RE.search(texto)
        url = encontrado.group(1).rstrip(".") if encontrado else ""
        antes = texto[: encontrado.start()].strip().rstrip(".").strip() if encontrado else texto

        autor_texto, resto = self._separar_autor(antes)
        titulo = resto if autor_texto else antes
        return self.format_website(author=autor_texto, title=titulo, url=url)

    def _analisar_livro(self, texto: str) -> Referencia:
        """Extrai autor, título, edição e imprenta de um texto de livro."""
        autor_texto, resto = self._separar_autor(texto)

        cidade = editora = ""
        ano: int | None = None
        imprenta = _IMPRENTA_RE.search(resto)
        if imprenta:
            cidade = imprenta.group(1).strip()
            editora = imprenta.group(2).strip()
            ano = int(imprenta.group(3))
            antes = resto[: imprenta.start()].strip().rstrip(".").strip()
        else:
            antes = resto.strip()

        edicao = ""
        encontrado_edicao = _EDICAO_RE.search(antes)
        if encontrado_edicao:
            edicao = encontrado_edicao.group(1)
            antes = (antes[: encontrado_edicao.start()] + antes[encontrado_edicao.end() :]).strip(
                " ."
            )

        return self.format_book(
            author=autor_texto,
            title=antes.strip().rstrip("."),
            edition=edicao,
            city=cidade,
            publisher=editora,
            year=ano,
        )

    def _analisar_artigo(self, texto: str) -> Referencia:
        """Extrai autor, título, periódico e detalhes de um artigo."""
        autor_texto, resto = self._separar_autor(texto)

        volume = _VOLUME_RE.search(resto)
        numero = _NUMERO_RE.search(resto)
        paginas = _PAGINAS_RE.search(resto)
        ano = _ANO_RE.search(resto)

        corte = len(resto)
        for encontrado in (volume, numero, paginas):
            if encontrado:
                corte = min(corte, encontrado.start())

        cabeca = resto[:corte].strip().rstrip(",").strip()
        partes = [parte.strip() for parte in cabeca.split(",") if parte.strip()]
        cidade = ""
        if len(partes) >= 2:
            cidade = partes[-1]
            cabeca = ", ".join(partes[:-1])

        if ". " in cabeca:
            artigo, periodico = cabeca.rsplit(". ", 1)
        else:
            artigo, periodico = cabeca, ""

        return self.format_journal_article(
            author=autor_texto,
            article_title=artigo.strip(),
            journal_title=periodico.strip(),
            city=cidade,
            volume=volume.group(1) if volume else "",
            number=numero.group(1) if numero else "",
            pages=paginas.group(1) if paginas else "",
            year=int(ano.group(1)) if ano else None,
        )

    # ── Ordenação ───────────────────────────────────────────────────────────

    def sort_references(
        self, ref_list: Iterable[Referencia | str]
    ) -> list[Referencia | str]:
        """Ordena as referências em ordem alfabética estrita, como exige a ABNT.

        Aceita objetos :class:`Referencia` ou textos simples.
        """

        def chave(item: Referencia | str) -> str:
            if isinstance(item, Referencia):
                return item.chave_ordenacao()
            return normalizar_para_ordenacao(re.sub(r"[*_]", "", str(item)))

        return sorted(ref_list, key=chave)
