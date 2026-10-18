"""Gerador de PDF a partir de DOCX.

Converte o documento DOCX gerado para PDF usando:
- docx2pdf (Windows/Mac com Word instalado)
- LibreOffice headless (Linux / fallback)
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from src.core.exceptions import GeneratorError


class PdfGenerator:
    """Gera PDF convertendo de DOCX."""

    def gerar(self, documento, caminho: Path) -> Path:
        """Gera PDF a partir de um DOCX já gerado.

        Args:
            documento: Documento (não utilizado diretamente — o PDF é
                       gerado a partir do DOCX intermediário).
            caminho: Caminho de saída do PDF.

        Returns:
            Path do PDF gerado.
        """
        try:
            # Primeiro gera o DOCX temporário
            from src.generators.docx_generator import DocxGenerator

            docx_gen = DocxGenerator()
            docx_temp = caminho.with_suffix(".docx")
            docx_gen.gerar(documento, docx_temp)

            # Converte para PDF
            pdf_path = self._converter_para_pdf(docx_temp, caminho)

            # Remove DOCX temporário se for diferente do destino
            if docx_temp.exists() and docx_temp != caminho.with_suffix(".docx"):
                docx_temp.unlink()

            return pdf_path

        except GeneratorError:
            raise
        except Exception as e:
            raise GeneratorError(f"Erro ao gerar PDF: {e}") from e

    def _converter_para_pdf(self, docx_path: Path, pdf_path: Path) -> Path:
        """Converte DOCX para PDF usando o método disponível."""
        # Tentar docx2pdf (Windows/Mac)
        try:
            from docx2pdf import convert

            convert(str(docx_path), str(pdf_path))
            return pdf_path
        except ImportError:
            pass
        except Exception:
            pass

        # Tentar LibreOffice headless (Linux/fallback)
        try:
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(pdf_path.parent),
                    str(docx_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                # LibreOffice gera com nome baseado no arquivo original
                pdf_gerado = docx_path.with_suffix(".pdf")
                if pdf_gerado != pdf_path:
                    pdf_gerado.rename(pdf_path)
                return pdf_path
        except FileNotFoundError:
            pass

        raise GeneratorError(
            "Não foi possível converter para PDF. "
            "Instale 'docx2pdf' (pip install docx2pdf) ou "
            "LibreOffice no sistema."
        )