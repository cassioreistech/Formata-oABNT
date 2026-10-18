"""Validador de estrutura de documentos ABNT.

Verifica conformidade com NBR 14724 e normas relacionadas.
"""

from __future__ import annotations

from src.core.config import ESTRUTURA_DOCUMENTO, TipoDocumento
from src.core.models import Documento


def validar_documento(documento: Documento) -> list[str]:
    """Valida a estrutura do documento conforme normas ABNT.

    Args:
        documento: Documento a ser validado.

    Returns:
        Lista de mensagens de erro. Lista vazia = documento válido.
    """
    erros: list[str] = []
    meta = documento.metadados

    # Validar campos obrigatórios dos metadados
    erros.extend(_validar_metadados(meta))

    # Validar estrutura por tipo de documento
    erros.extend(_validar_estrutura(documento))

    # Validar referências
    erros.extend(_validar_referencias(documento))

    # Validar seções
    erros.extend(_validar_secoes(documento))

    return erros


def _validar_metadados(meta) -> list[str]:
    """Valida metadados obrigatórios."""
    erros = []

    if not meta.titulo or not meta.titulo.strip():
        erros.append("Título do documento é obrigatório (NBR 14724)")

    if not meta.autores:
        erros.append("Pelo menos um autor é obrigatório (NBR 14724)")

    if not meta.instituicao or not meta.instituicao.strip():
        erros.append("Instituição é obrigatória na folha de rosto (NBR 14724)")

    if not meta.cidade or not meta.cidade.strip():
        erros.append("Cidade é obrigatória na folha de rosto (NBR 14724)")

    if not meta.ano:
        erros.append("Ano é obrigatório na folha de rosto (NBR 14724)")

    return erros


def _validar_estrutura(documento: Documento) -> list[str]:
    """Valida estrutura de seções por tipo de documento."""
    erros = []
    tipo = documento.metadados.tipo

    estrutura = ESTRUTURA_DOCUMENTO.get(tipo)
    if not estrutura:
        return erros

    # Verificar se tem seções textuais
    if not documento.secoes:
        erros.append(f"Documento do tipo '{tipo.value}' deve ter seções textuais")

    # Verificar introdução
    titulos_secoes = [s.titulo.lower() for s in documento.secoes]
    if documento.secoes and "introdução" not in titulos_secoes and "introducao" not in titulos_secoes:
        erros.append("Documento deve iniciar com Introdução (NBR 14724)")

    return erros


def _validar_referencias(documento: Documento) -> list[str]:
    """Valida referências bibliográficas."""
    erros = []

    if not documento.referencias:
        erros.append("Documento deve ter pelo menos uma referência (NBR 6023)")
        return erros

    for i, ref in enumerate(documento.referencias, start=1):
        if not ref.autores:
            erros.append(f"Referência {i}: autor(es) é obrigatório (NBR 6023)")
        if not ref.titulo or not ref.titulo.strip():
            erros.append(f"Referência {i}: título é obrigatório (NBR 6023)")
        if not ref.ano:
            erros.append(f"Referência {i}: ano é obrigatório (NBR 6023)")

    return erros


def _validar_secoes(documento: Documento) -> list[str]:
    """Valida seções individuais."""
    erros = []

    for i, secao in enumerate(documento.secoes):
        if not secao.titulo or not secao.titulo.strip():
            erros.append(f"Seção {i + 1}: título não pode estar vazio")
        if not secao.conteudo and not secao.subsecoes:
            erros.append(
                f"Seção '{secao.titulo}': deve ter conteúdo ou subseções"
            )

    return erros