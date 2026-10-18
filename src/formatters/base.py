"""Classe base abstrata para formatters de documentos ABNT."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.models import Documento


class BaseFormatter(ABC):
    """Interface base para todos os formatters.

    Cada tipo de documento (TCC, Artigo, Tese, etc.) implementa
    esta classe com suas regras específicas de formatação.
    """

    @abstractmethod
    def formatar(self, documento: Documento) -> Documento:
        """Aplica regras de formatação ABNT específicas do tipo de documento.

        Args:
            documento: Documento original a ser formatado.

        Returns:
            Documento com formatação aplicada.
        """

    def _numerar_secoes(self, documento: Documento) -> Documento:
        """Aplica numeração progressiva às seções (NBR 6024)."""
        for i, secao in enumerate(documento.secoes, start=1):
            secao.numeracao = str(i)
            self._numerar_subsecoes(secao, prefixo=str(i))
        return documento

    def _numerar_subsecoes(self, secao, prefixo: str) -> None:
        """Numera subseções recursivamente."""
        for i, sub in enumerate(secao.subsecoes, start=1):
            sub.numeracao = f"{prefixo}.{i}"
            self._numerar_subsecoes(sub, prefixo=sub.numeracao)

    def _numerar_figuras(self, documento: Documento) -> Documento:
        """Numera figuras sequencialmente."""
        for i, fig in enumerate(documento.figuras, start=1):
            fig.numeracao = f"Figura {i}"
        return documento

    def _numerar_tabelas(self, documento: Documento) -> Documento:
        """Numera tabelas sequencialmente."""
        for i, tab in enumerate(documento.tabelas, start=1):
            tab.numeracao = f"Tabela {i}"
        return documento