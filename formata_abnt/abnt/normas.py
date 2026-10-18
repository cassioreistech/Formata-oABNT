"""Parâmetros de formatação exigidos pela NBR 14724."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormasABNT:
    """Layout de um trabalho acadêmico conforme a NBR 14724.

    Todos os valores são os padrões mais usados; qualquer um pode ser
    sobrescrito para atender a exigências específicas da instituição.
    """

    # Margens (cm)
    margem_superior_cm: float = 3.0
    margem_inferior_cm: float = 2.0
    margem_esquerda_cm: float = 3.0
    margem_direita_cm: float = 2.0

    # Fonte do corpo do texto
    fonte_corpo: str = "Times New Roman"
    tamanho_corpo_pt: int = 12

    # Fonte dos títulos
    fonte_titulo: str = "Times New Roman"
    tamanho_titulo_pt: int = 12

    # Parágrafo
    espacamento_linhas: float = 1.5
    recuo_primeira_linha_cm: float = 1.25


PADRAO = NormasABNT()
