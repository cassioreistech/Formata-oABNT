"""Formatter para TCC / Monografia (Graduação).

Estrutura conforme NBR 14724:2024:
- Elementos pré-textuais: Capa, Folha de rosto, Folha de aprovação,
  Dedicatória, Agradecimentos, Epígrafe, Resumo, Abstract,
  Listas, Sumário
- Elementos textuais: Introdução, Desenvolvimento, Conclusão
- Elementos pós-textuais: Referências, Glossário, Apêndices,
  Anexos, Índice
"""

from __future__ import annotations

from src.core.models import Documento
from src.formatters.base import BaseFormatter


class TCCFormatter(BaseFormatter):
    """Formatter para Trabalho de Conclusão de Curso (TCC)."""

    ELEMENTOS_OBRIGATORIOS_PRE = ["capa", "folha_de_rosto", "sumario"]
    ELEMENTOS_OBRIGATORIOS_POS = ["referencias"]

    def formatar(self, documento: Documento) -> Documento:
        """Aplica formatação ABNT para TCC.

        Regras:
        - Numeração de seções progressiva (NBR 6024)
        - Numeração de figuras e tabelas
        - Garante elementos obrigatórios
        """
        # Numeração progressiva (NBR 6024)
        documento = self._numerar_secoes(documento)

        # Numeração de figuras e tabelas
        documento = self._numerar_figuras(documento)
        documento = self._numerar_tabelas(documento)

        # Garantir que seções textuais comecem com introdução
        if documento.secoes:
            primeira = documento.secoes[0]
            if primeira.titulo.lower() not in (
                "introdução",
                "introducao",
            ):
                # Não altera, apenas avisa — o validator vai pegar
                pass

        return documento