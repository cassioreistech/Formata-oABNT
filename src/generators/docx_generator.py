"""Gerador de documentos DOCX com formatação ABNT.

Utiliza python-docx para criar documentos .docx com:
- Margens conforme NBR 14724
- Fontes e tamanhos corretos
- Espaçamento entre linhas
- Numeração de páginas
- Estilos para títulos, corpo, citações, referências
- Capa, folha de rosto, sumário
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt

from src.core.config import Citacao, Formatacao, Referencias
from src.core.exceptions import GeneratorError
from src.core.models import (
    Documento,
    Figura,
    Referencia,
    Secao,
    Tabela,
    TipoCitacao,
)
from src.generators.styles import (
    ESTILO_CORPO,
    ESTILO_LEGENDA,
    ESTILO_RESUMO,
    ESTILO_TITULO_NIVEL_1,
    ESTILOS_TITULO,
    EstiloParagrafo,
)


class DocxGenerator:
    """Gera documentos .docx com formatação ABNT."""

    def gerar(self, documento: Documento, caminho: Path) -> Path:
        """Gera o arquivo DOCX.

        Args:
            documento: Documento formatado.
            caminho: Caminho de saída do arquivo.

        Returns:
            Path do arquivo gerado.
        """
        try:
            doc = Document()
            self._configurar_margens(doc)
            self._configurar_estilos(doc)

            # Elementos pré-textuais
            self._gerar_capa(doc, documento)
            self._gerar_folha_de_rosto(doc, documento)

            if documento.resumo:
                self._gerar_resumo(doc, documento)
            if documento.abstract:
                self._gerar_abstract(doc, documento)

            if documento.referencias:
                self._gerar_sumario_placeholder(doc)

            # Elementos textuais
            for secao in documento.secoes:
                self._gerar_secao(doc, secao)

            # Figuras e tabelas inline
            # (geradas junto com as seções no futuro)

            # Elementos pós-textuais
            if documento.referencias:
                self._gerar_referencias(doc, documento.referencias)

            if documento.apendices:
                for ap in documento.apendices:
                    self._gerar_secao(doc, ap, prefixo="APÊNDICE")

            if documento.anexos:
                for an in documento.anexos:
                    self._gerar_secao(doc, an, prefixo="ANEXO")

            # Salvar
            caminho.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(caminho))
            return caminho

        except Exception as e:
            if isinstance(e, GeneratorError):
                raise
            raise GeneratorError(f"Erro ao gerar DOCX: {e}") from e

    # ── Configuração ────────────────────────────────────────────────────────

    def _configurar_margens(self, doc: Document) -> None:
        """Configura margens conforme NBR 14724."""
        for section in doc.sections:
            section.top_margin = Cm(Formatacao.MARGEM_SUPERIOR)
            section.bottom_margin = Cm(Formatacao.MARGEM_INFERIOR)
            section.left_margin = Cm(Formatacao.MARGEM_ESQUERDA)
            section.right_margin = Cm(Formatacao.MARGEM_DIREITA)

    def _configurar_estilos(self, doc: Document) -> None:
        """Configura estilos base no documento."""
        style = doc.styles["Normal"]
        font = style.font
        font.name = Formatacao.FONTE_PADRAO
        font.size = Pt(Formatacao.TAMANHO_FONTE)

        paragraph_format = style.paragraph_format
        paragraph_format.line_spacing = Formatacao.ESPACAMENTO_LINHAS
        paragraph_format.space_after = Pt(0)
        paragraph_format.space_before = Pt(0)

    # ── Parágrafos ──────────────────────────────────────────────────────────

    def _adicionar_paragrafo(
        self,
        doc: Document,
        texto: str,
        estilo: EstiloParagrafo | None = None,
        fonte: str | None = None,
        tamanho: int | None = None,
        negrito: bool = False,
        italico: bool = False,
        alinhamento: WD_ALIGN_PARAGRAPH | None = None,
    ) -> None:
        """Adiciona um parágrafo ao documento com estilo ABNT."""
        p = doc.add_paragraph()
        run = p.add_run(texto)

        # Aplicar estilo base
        if estilo:
            run.font.name = estilo.fonte
            run.font.size = Pt(estilo.tamanho)
            run.bold = estilo.negrito or negrito
            run.italic = estilo.italico or italico
            p.paragraph_format.line_spacing = estilo.espacamento
            p.paragraph_format.alignment = (
                alinhamento or estilo.alinhamento
            )

            if estilo.indentacao_esquerda is not None:
                p.paragraph_format.left_indent = Cm(estilo.indentacao_esquerda)
            if estilo.indentacao_primeira_linha is not None:
                p.paragraph_format.first_line_indent = Cm(
                    estilo.indentacao_primeira_linha
                )

            if estilo.espaco_antes:
                p.paragraph_format.space_before = Pt(estilo.espaco_antes)
            if estilo.espaco_depois:
                p.paragraph_format.space_after = Pt(estilo.espaco_depois)

            if estilo.maiusculas:
                run.font.name = estilo.fonte
                # python-docx não tem uppercase nativo, mas podemos
                # transformar o texto
                run.text = texto.upper()
        else:
            run.font.name = fonte or Formatacao.FONTE_PADRAO
            run.font.size = Pt(tamanho or Formatacao.TAMANHO_FONTE)
            run.bold = negrito
            run.italic = italico
            p.paragraph_format.alignment = alinhamento or WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = Formatacao.ESPACAMENTO_LINHAS

    def _adicionar_espaco(self, doc: Document, linhas: int = 1) -> None:
        """Adiciona linhas em branco."""
        for _ in range(linhas):
            doc.add_paragraph()

    # ── Capa ────────────────────────────────────────────────────────────────

    def _gerar_capa(self, doc: Document, documento: Documento) -> None:
        """Gera a capa conforme NBR 14724."""
        meta = documento.metadados

        self._adicionar_espaco(doc, 6)

        self._adicionar_paragrafo(
            doc,
            meta.instituicao.upper(),
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            negrito=True,
        )

        self._adicionar_espaco(doc, 2)

        # Autores
        for autor in meta.autores:
            self._adicionar_paragrafo(
                doc,
                autor.nome_completo.upper(),
                alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
                negrito=True,
            )

        self._adicionar_espaco(doc, 6)

        # Título
        titulo = meta.titulo.upper()
        if meta.subtitulo:
            titulo += f": {meta.subtitulo.upper()}"
        self._adicionar_paragrafo(
            doc,
            titulo,
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            negrito=True,
        )

        self._adicionar_espaco(doc, 8)

        # Cidade e ano
        local = meta.cidade
        if meta.estado:
            local += f" - {meta.estado}"
        self._adicionar_paragrafo(
            doc,
            str(meta.ano),
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
        )

        doc.add_page_break()

    # ── Folha de rosto ──────────────────────────────────────────────────────

    def _gerar_folha_de_rosto(self, doc: Document, documento: Documento) -> None:
        """Gera a folha de rosto."""
        meta = documento.metadados

        self._adicionar_espaco(doc, 6)

        # Autores
        for autor in meta.autores:
            self._adicionar_paragrafo(
                doc,
                autor.nome_completo.upper(),
                alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
                negrito=True,
            )

        self._adicionar_espaco(doc, 6)

        # Título
        titulo = meta.titulo.upper()
        if meta.subtitulo:
            titulo += f": {meta.subtitulo.upper()}"
        self._adicionar_paragrafo(
            doc,
            titulo,
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            negrito=True,
        )

        self._adicionar_espaco(doc, 4)

        # Tipo de documento + área
        tipo_texto = {
            "tcc": "Trabalho de Conclusão de Curso",
            "artigo": "Artigo Científico",
            "dissertacao": "Dissertação",
            "tese": "Tese",
            "relatorio": "Relatório Técnico",
            "projeto_pesquisa": "Projeto de Pesquisa",
        }
        texto_tipo = tipo_texto.get(meta.tipo.value, "")
        if meta.curso:
            texto_tipo += f" — {meta.curso}"
        if texto_tipo:
            self._adicionar_paragrafo(
                doc,
                texto_tipo,
                alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
                italico=True,
            )

        self._adicionar_espaco(doc, 8)

        # Orientador
        if meta.orientador:
            self._adicionar_paragrafo(
                doc,
                f"Orientador: {meta.orientador}",
                alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            )
        if meta.coorientador:
            self._adicionar_paragrafo(
                doc,
                f"Coorientador: {meta.coorientador}",
                alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            )

        self._adicionar_espaco(doc, 4)

        # Local e ano
        local = meta.cidade
        if meta.estado:
            local += f" - {meta.estado}"
        self._adicionar_paragrafo(
            doc,
            local,
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
        )
        self._adicionar_paragrafo(
            doc,
            str(meta.ano),
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
        )

        doc.add_page_break()

    # ── Resumo ──────────────────────────────────────────────────────────────

    def _gerar_resumo(self, doc: Document, documento: Documento) -> None:
        """Gera o resumo conforme NBR 6028."""
        self._adicionar_paragrafo(
            doc,
            "RESUMO",
            estilo=ESTILO_TITULO_NIVEL_1,
        )
        self._adicionar_paragrafo(
            doc,
            documento.resumo,
            estilo=ESTILO_RESUMO,
        )

        # Palavras-chave
        if documento.metadados.palavras_chave:
            pchave = "Palavras-chave: " + "; ".join(documento.metadados.palavras_chave)
            self._adicionar_paragrafo(
                doc,
                pchave,
                estilo=ESTILO_RESUMO,
                negrito=False,
            )

        doc.add_page_break()

    def _gerar_abstract(self, doc: Document, documento: Documento) -> None:
        """Gera o abstract."""
        self._adicionar_paragrafo(
            doc,
            "ABSTRACT",
            estilo=ESTILO_TITULO_NIVEL_1,
        )
        self._adicionar_paragrafo(
            doc,
            documento.abstract,
            estilo=ESTILO_RESUMO,
        )
        doc.add_page_break()

    # ── Sumário placeholder ─────────────────────────────────────────────────

    def _gerar_sumario_placeholder(self, doc: Document) -> None:
        """Placeholder para sumário (a ser gerado automaticamente)."""
        self._adicionar_paragrafo(
            doc,
            "SUMÁRIO",
            estilo=ESTILO_TITULO_NIVEL_1,
        )
        self._adicionar_paragrafo(
            doc,
            "[Sumário — gerado automaticamente pelo Word após formatação]",
            alinhamento=WD_ALIGN_PARAGRAPH.CENTER,
            italico=True,
        )
        doc.add_page_break()

    # ── Seções ──────────────────────────────────────────────────────────────

    def _gerar_secao(
        self,
        doc: Document,
        secao: Secao,
        prefixo: str = "",
    ) -> None:
        """Gera uma seção com título e conteúdo."""
        # Título
        nivel = min(secao.nivel.value, 4)
        estilo_titulo = ESTILOS_TITULO.get(nivel, ESTILO_TITULO_NIVEL_1)

        titulo_texto = secao.titulo
        if secao.numeracao and not prefixo:
            titulo_texto = f"{secao.numeracao} {titulo_texto}"
        elif prefixo:
            titulo_texto = f"{prefixo} — {titulo_texto}"

        self._adicionar_paragrafo(
            doc,
            titulo_texto,
            estilo=estilo_titulo,
        )

        # Conteúdo (parágrafos)
        for paragrafo in secao.conteudo:
            # Verificar se é citação longa
            if paragrafo.strip().startswith(">") or len(paragrafo) > 500:
                # Provável citação longa
                self._gerar_citacao_longa(doc, paragrafo)
            else:
                self._adicionar_paragrafo(doc, paragrafo, estilo=ESTILO_CORPO)

        # Subsecoes
        for sub in secao.subsecoes:
            self._gerar_secao(doc, sub)

    # ── Citações ────────────────────────────────────────────────────────────

    def _gerar_citacao_longa(self, doc: Document, texto: str) -> None:
        """Gera citação longa em bloco (NBR 10520)."""
        # Remove o '>' se houver
        texto_limpo = texto.lstrip("> ").strip()
        self._adicionar_paragrafo(
            doc,
            texto_limpo,
            tamanho=10,
            espacamento=1.0,
            indentacao_esquerda=4.0,
        )

    # ── Referências ─────────────────────────────────────────────────────────

    def _gerar_referencias(self, doc: Document, referencias: list[Referencia]) -> None:
        """Gera a seção de referências conforme NBR 6023."""
        self._adicionar_paragrafo(
            doc,
            "REFERÊNCIAS",
            estilo=ESTILO_TITULO_NIVEL_1,
        )

        # Ordenar por autor
        refs_ordenadas = sorted(referencias, key=lambda r: r.autores[0] if r.autores else "")

        for ref in refs_ordenadas:
            texto = self._formatar_referencia(ref)
            # Hanging indent (indentação francesa)
            self._adicionar_paragrafo(
                doc,
                texto,
                estilo=ESTILO_CORPO,
                indentacao_primeira_linha=-1.25,  # Negativo = hanging
                indentacao_esquerda=1.25,
            )

    def _formatar_referencia(self, ref: Referencia) -> str:
        """Formata uma referência conforme NBR 6023."""
        autores = "; ".join(ref.autores)
        partes = [autores]

        if ref.tipo == "livro":
            partes.append(ref.titulo)
            if ref.subtitulo:
                partes[1] += f": {ref.subtitulo}"
            if ref.edicao:
                partes.append(f"{ref.edicao} ed.")
            if ref.local and ref.editora:
                partes.append(f"{ref.local}: {ref.editora}")
            elif ref.editora:
                partes.append(ref.editora)
            partes.append(str(ref.ano))

        elif ref.tipo == "artigo_periodico":
            partes.append(ref.titulo)
            if ref.revista:
                partes.append(ref.revista)
            if ref.volume:
                partes[-1] += f", v. {ref.volume}"
            if ref.numero:
                partes[-1] += f", n. {ref.numero}"
            if ref.paginas:
                partes[-1] += f", {ref.paginas}"
            if ref.ano:
                partes[-1] += f", {ref.ano}"
            if ref.doi:
                partes.append(f"DOI: {ref.doi}")

        elif ref.tipo == "documento_eletronico":
            partes.append(ref.titulo)
            if ref.local or ref.editora:
                local = ref.local or "[S.l.]"
                editora = ref.editora or "[s.n.]"
                partes.append(f"{local}: {editora}")
            if ref.ano:
                partes.append(str(ref.ano))
            if ref.url:
                partes.append(f"Disponível em: {ref.url}")
            if ref.data_acesso:
                partes.append(f"Acesso em: {ref.data_acesso.strftime('%d %b %Y')}")

        else:
            # Formato genérico
            partes.append(ref.titulo)
            if ref.editora:
                partes.append(ref.editora)
            partes.append(str(ref.ano))

        return ". ".join(partes) + "."