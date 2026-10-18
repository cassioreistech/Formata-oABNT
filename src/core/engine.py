"""Motor principal de formatação ABNT.

Orquestra o fluxo: Documento → Formatter → Validator → Generator → Saída.
"""

from __future__ import annotations

from pathlib import Path

from src.core.config import TipoDocumento
from src.core.exceptions import DocumentTypeError, GeneratorError
from src.core.models import Documento


# Registry de generators (lazy import para evitar circularidade)
_GENERATORS: dict[str, type] = {}


def _get_generator(formato: str):
    """Importa e retorna o generator pelo formato."""
    if formato == "docx":
        from src.generators.docx_generator import DocxGenerator

        return DocxGenerator()
    elif formato == "pdf":
        from src.generators.pdf_generator import PdfGenerator

        return PdfGenerator()
    else:
        raise GeneratorError(f"Formato de saída não suportado: {formato}")


def _get_formatter(tipo: TipoDocumento):
    """Importa e retorna o formatter pelo tipo de documento."""
    formatters = {
        TipoDocumento.TCC: "src.formatters.tcc",
        TipoDocumento.ARTIGO: "src.formatters.artigo",
        TipoDocumento.DISSERTACAO: "src.formatters.dissertacao",
        TipoDocumento.TESE: "src.formatters.tese",
        TipoDocumento.RELATORIO: "src.formatters.relatorio",
        TipoDocumento.PROJETO_PESQUISA: "src.formatters.projeto_pesquisa",
    }

    module_path = formatters.get(tipo)
    if not module_path:
        raise DocumentTypeError(tipo.value)

    import importlib

    module = importlib.import_module(module_path)

    # Busca a classe formatter no módulo
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and hasattr(attr, "formatar")
            and attr_name.endswith("Formatter")
        ):
            return attr()

    raise DocumentTypeError(tipo.value)


class Engine:
    """Motor principal do sistema de formatação ABNT.

    Coordena o fluxo completo de geração de documentos:
    1. Recebe um Documento (modelo Pydantic)
    2. Aplica o formatter específico do tipo de documento
    3. Valida a conformidade com as normas ABNT
    4. Gera a saída no formato desejado (DOCX/PDF)
    """

    def formatar(
        self,
        documento: Documento,
        formato: str = "docx",
        caminho_saida: str | Path | None = None,
        validar: bool = True,
    ) -> Path:
        """Formata e gera o documento.

        Args:
            documento: Modelo do documento a ser formatado.
            formato: Formato de saída ("docx" ou "pdf").
            caminho_saida: Caminho do arquivo de saída. Se None, gera automaticamente.
            validar: Se True, valida conformidade antes de gerar.

        Returns:
            Path do arquivo gerado.

        Raises:
            ValidationError: Se validar=True e houver não-conformidades.
            GeneratorError: Se houver erro na geração.
        """
        # 1. Validar (opcional)
        if validar:
            from src.validators.structure import validar_documento

            erros = validar_documento(documento)
            if erros:
                raise GeneratorError(
                    f"Documento com {len(erros)} erro(s) de validação:\n"
                    + "\n".join(f"  - {e}" for e in erros)
                )

        # 2. Aplicar formatter
        formatter = _get_formatter(documento.metadados.tipo)
        documento_formatado = formatter.formatar(documento)

        # 3. Gerar saída
        generator = _get_generator(formato)

        if caminho_saida is None:
            titulo_slug = (
                documento.metadados.titulo.lower()
                .replace(" ", "_")
                .replace("/", "-")[:50]
            )
            caminho_saida = Path(f"{titulo_slug}.{formato}")

        caminho_saida = Path(caminho_saida)
        return generator.gerar(documento_formatado, caminho_saida)