"""Sanitização de texto copiado da web/PDF e limpeza estrutural."""

from __future__ import annotations

import re
from dataclasses import dataclass

from docx.document import Document as DocumentoDocx
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

# Caracteres invisíveis ou típicos de cópia que devem ser normalizados.
_INVISIVEIS = {
    "\u00a0": " ",  # espaço inseparável
    "\u2007": " ",  # espaço de figura
    "\u202f": " ",  # espaço estreito inseparável
    "\u200b": "",  # largura zero
    "\u200c": "",
    "\u200d": "",
    "\ufeff": "",  # marca de ordem de bytes
    "\u00ad": "",  # hífen suave
    "\u2028": " ",  # separador de linha
    "\u2029": " ",
}

_ESPACOS_REPETIDOS = re.compile(r"[ \t]{2,}")
_TIPOS_QUEBRA_REMOVIVEL = (None, "textWrapping")


@dataclass
class ResultadoSanitizacao:
    """Contagem do que foi limpo durante a sanitização."""

    runs_limpos: int = 0
    paragrafos_removidos: int = 0
    quebras_removidas: int = 0


def limpar_texto(texto: str) -> str:
    """Remove artefatos invisíveis e colapsa espaços/tabelas repetidos."""
    for origem, destino in _INVISIVEIS.items():
        texto = texto.replace(origem, destino)
    return _ESPACOS_REPETIDOS.sub(" ", texto)


def limpar_runs(documento: DocumentoDocx) -> int:
    """Aplica :func:`limpar_texto` ao texto dos runs e devolve quantos mudaram."""
    alterados = 0
    for paragrafo in documento.paragraphs:
        for run in paragrafo.runs:
            original = run.text
            limpo = limpar_texto(original)
            if limpo != original:
                run.text = limpo
                alterados += 1
    return alterados


def remover_quebras_repetidas(documento: DocumentoDocx) -> int:
    """Remove quebras de linha repetidas, preservando quebras de página."""
    removidas = 0
    for paragrafo in documento.paragraphs:
        quebra_anterior = False
        for run in paragrafo.runs:
            for quebra in list(run._element.findall(qn("w:br"))):
                tipo = quebra.get(qn("w:type"))
                if tipo not in _TIPOS_QUEBRA_REMOVIVEL:
                    quebra_anterior = False
                    continue
                if quebra_anterior:
                    run._element.remove(quebra)
                    removidas += 1
                else:
                    quebra_anterior = True
    return removidas


def remover_paragrafos_vazios_repetidos(documento: DocumentoDocx) -> int:
    """Remove parágrafos vazios consecutivos, mantendo no máximo um."""
    removidos = 0
    vazio_anterior = False
    for paragrafo in list(documento.paragraphs):
        vazio = not paragrafo.text.strip()
        if vazio and vazio_anterior and _pode_remover(paragrafo, documento):
            paragrafo._element.getparent().remove(paragrafo._element)
            removidos += 1
            continue
        vazio_anterior = vazio
    return removidos


def sanitizar(documento: DocumentoDocx) -> ResultadoSanitizacao:
    """Executa a sanitização completa do documento."""
    runs = limpar_runs(documento)
    quebras = remover_quebras_repetidas(documento)
    paragrafos = remover_paragrafos_vazios_repetidos(documento)
    return ResultadoSanitizacao(runs, paragrafos, quebras)


def _pode_remover(paragrafo: Paragraph, documento: DocumentoDocx) -> bool:
    """Impede que o corpo do documento fique sem nenhum parágrafo."""
    return len(documento.paragraphs) > 1
