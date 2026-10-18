"""Motor ABNT: sanitização e reformatação de arquivos .docx.

Pipeline: ler -> sanitizar -> títulos -> citações -> tipografia -> margens
-> referências -> salvar.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from formata_abnt import sanitizador
from formata_abnt.caminhos import nome_saida_padrao
from formata_abnt.citacao_longa import aplicar_citacoes_longas
from formata_abnt.docx_io import abrir, salvar
from formata_abnt.margens import aplicar_margens
from formata_abnt.normas import PADRAO, NormasABNT
from formata_abnt.referencias import formatar_secao_referencias
from formata_abnt.tipografia import aplicar_tipografia_corpo, definir_estilo_normal
from formata_abnt.titulos import aplicar_titulos

ProgressoCallback = Callable[[str], None]


@dataclass
class ResultadoFormatacao:
    """Resumo do que foi aplicado em uma execução."""

    arquivo_saida: Path
    titulos_aplicados: int
    citacoes_aplicadas: int
    paragrafos_formatados: int
    runs_sanitizados: int
    paragrafos_removidos: int
    referencias_ordenadas: int = 0


def _notificar(progresso: ProgressoCallback | None, mensagem: str) -> None:
    """Dispara o callback de progresso quando informado."""
    if progresso is not None:
        progresso(mensagem)


class MotorABNT:
    """Executa o pipeline completo de formatação ABNT em um .docx."""

    def __init__(self, normas: NormasABNT = PADRAO) -> None:
        self.normas = normas

    def processar(
        self,
        entrada: str | Path,
        saida: str | Path | None = None,
        progresso: ProgressoCallback | None = None,
    ) -> ResultadoFormatacao:
        """Reformata o documento de ``entrada`` e grava em ``saida``."""
        origem = Path(entrada)
        destino = Path(saida) if saida else nome_saida_padrao(origem)

        _notificar(progresso, "Lendo documento...")
        documento = abrir(origem)

        _notificar(progresso, "Sanitizando texto...")
        resultado_sanitizacao = sanitizador.sanitizar(documento)

        _notificar(progresso, "Identificando títulos e subtítulos...")
        titulos = aplicar_titulos(documento, self.normas)

        _notificar(progresso, "Detectando citações longas...")
        citacoes = aplicar_citacoes_longas(documento, self.normas)

        _notificar(progresso, "Aplicando tipografia ABNT...")
        paragrafos = aplicar_tipografia_corpo(documento, self.normas)

        _notificar(progresso, "Aplicando margens ABNT...")
        aplicar_margens(documento, self.normas)
        definir_estilo_normal(documento, self.normas)

        _notificar(progresso, "Ordenando referências (NBR 6023)...")
        referencias = formatar_secao_referencias(documento, self.normas)

        _notificar(progresso, "Salvando documento...")
        arquivo_saida = salvar(documento, destino)

        _notificar(progresso, "Concluído!")
        return ResultadoFormatacao(
            arquivo_saida=arquivo_saida,
            titulos_aplicados=titulos,
            citacoes_aplicadas=citacoes,
            paragrafos_formatados=paragrafos,
            runs_sanitizados=resultado_sanitizacao.runs_limpos,
            paragrafos_removidos=resultado_sanitizacao.paragrafos_removidos,
            referencias_ordenadas=referencias,
        )


def formatar_para_abnt(
    entrada: str | Path,
    saida: str | Path | None = None,
    normas: NormasABNT = PADRAO,
    progresso: ProgressoCallback | None = None,
) -> ResultadoFormatacao:
    """Atalho funcional para reformatar um único arquivo .docx."""
    return MotorABNT(normas).processar(entrada, saida, progresso)
