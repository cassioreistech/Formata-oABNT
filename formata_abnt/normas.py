"""Parâmetros de formatação ABNT (NBR 14724 e NBR 10520)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormasABNT:
    """Conjunto de regras aplicadas a um documento acadêmico.

    Os valores padrão seguem as normas ABNT mais utilizadas; cada campo
    pode ser sobrescrito conforme exigência da instituição.
    """

    # Papel e margens (cm)
    largura_papel_cm: float = 21.0
    altura_papel_cm: float = 29.7
    margem_superior_cm: float = 3.0
    margem_inferior_cm: float = 2.0
    margem_esquerda_cm: float = 3.0
    margem_direita_cm: float = 2.0

    # Tipografia do corpo
    fonte_corpo: str = "Arial"
    tamanho_corpo_pt: int = 12
    espacamento_linhas: float = 1.5
    recuo_primeira_linha_cm: float = 1.25

    # Tipografia dos títulos (NBR 6024)
    fonte_titulo: str = "Arial"
    tamanho_titulo_pt: int = 12

    # Citação longa (NBR 10520)
    nome_estilo_citacao: str = "ABNT_CitacaoLonga"
    recuo_citacao_cm: float = 4.0
    tamanho_citacao_pt: int = 10
    espacamento_citacao: float = 1.0
    max_linhas_citacao_curta: int = 3
    caracteres_por_linha: int = 65


PADRAO = NormasABNT()
