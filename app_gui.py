"""Interface gráfica (CustomTkinter) do Formata-oABNT.

Duas abas: "Formatar Documento" (seleção/arrastar de arquivo, formatação,
progresso e log) e "Referências ABNT" (gerador de referências NBR 6023,
cópia e inserção no .docx).
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from abnt_engine import MotorABNT, ResultadoFormatacao
from abnt_references import ABNTReferenceFormatter, Referencia
from formata_abnt import historico, referencias
from formata_abnt.caminhos import nome_saida_padrao
from formata_abnt.config import Preferencias, carregar_preferencias, salvar_preferencias
from formata_abnt.docx_io import abrir, salvar
from formata_abnt.normas import NormasABNT

try:  # Drag-and-drop é opcional; sem ele a GUI segue funcionando.
    from tkinterdnd2 import DND_FILES, TkinterDnD

    _DND_DISPONIVEL = True
except Exception:  # pragma: no cover - depende do ambiente
    _DND_DISPONIVEL = False


if _DND_DISPONIVEL:

    class _JanelaBase(ctk.CTk, TkinterDnD.DnDWrapper):  # type: ignore[misc]
        """Janela CustomTkinter com suporte a arrastar-e-soltar."""

        def __init__(self) -> None:
            super().__init__()
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:  # pragma: no cover - depende do ambiente
                pass

else:

    class _JanelaBase(ctk.CTk):  # type: ignore[no-redef]
        """Janela CustomTkinter sem arrastar-e-soltar."""


CORES = {
    "azul": "#2563eb",
    "azul_hover": "#1d4ed8",
    "verde": "#16a34a",
    "verde_hover": "#15803d",
    "cinza": "#4b5563",
    "cinza_hover": "#374151",
}

# Campos do formulário de referências por tipo de fonte.
CAMPOS_POR_TIPO: dict[str, list[tuple[str, str]]] = {
    "Livro": [
        ("autor", "Autor(es) — nome completo"),
        ("titulo", "Título do livro"),
        ("edicao", "Edição (ex.: 2)"),
        ("cidade", "Cidade"),
        ("editora", "Editora"),
        ("ano", "Ano"),
    ],
    "Artigo": [
        ("autor", "Autor(es) — nome completo"),
        ("titulo_artigo", "Título do artigo"),
        ("titulo_periodico", "Periódico / Revista"),
        ("cidade", "Cidade"),
        ("volume", "Volume"),
        ("numero", "Número"),
        ("paginas", "Páginas (ex.: 45-60)"),
        ("ano", "Ano"),
    ],
    "Site": [
        ("autor", "Autor(es) — opcional"),
        ("titulo", "Título da página"),
        ("site_nome", "Nome do site (opcional)"),
        ("url", "URL"),
        ("data_acesso", "Data de acesso (dd/mm/aaaa)"),
    ],
    "Texto bruto": [
        ("bruto", "Cole aqui o texto da referência"),
    ],
}

# Chave do formulário que usa o seletor dinâmico de vários autores.
CHAVE_AUTORES = "autor"


class AplicacaoABNT(_JanelaBase):
    """Janela principal da aplicação de formatação ABNT."""

    def __init__(self) -> None:
        super().__init__()

        self.preferencias: Preferencias = carregar_preferencias()
        self.arquivo_entrada: Path | None = None
        self.ultimo_resultado: ResultadoFormatacao | None = None
        self.formatador = ABNTReferenceFormatter()
        self.referencia_atual: Referencia | None = None
        self.campos_referencia: dict[str, ctk.CTkBaseClass] = {}
        self.autores: list[str] = []
        self.referencias_preparadas: list[Referencia] = []
        self.campo_autor: ctk.CTkEntry | None = None
        self.rotulo_autores: ctk.CTkLabel | None = None

        self.title("Formata-oABNT — Formatador de Documentos")
        self.geometry("860x700")
        self.minsize(760, 620)
        ctk.set_appearance_mode(self.preferencias.tema)

        self._montar_interface()
        self._configurar_drag_and_drop()

    # ── Interface ───────────────────────────────────────────────────────────

    def _montar_interface(self) -> None:
        """Constrói o cabeçalho e as abas da janela."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._montar_cabecalho()

        self.abas = ctk.CTkTabview(self)
        self.abas.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self._montar_aba_documento(self.abas.add("Formatar Documento"))
        self._montar_aba_referencias(self.abas.add("Referências ABNT"))

    def _montar_cabecalho(self) -> None:
        """Cabeçalho com título e alternador de tema."""
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        cabecalho.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cabecalho, text="Formata-oABNT", font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            cabecalho,
            text="Formatação de documentos Word nas normas ABNT",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            cabecalho,
            text="Tema",
            width=80,
            command=self._alternar_tema,
            fg_color="transparent",
            border_width=1,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

    # ── Aba: Formatar Documento ─────────────────────────────────────────────

    def _montar_aba_documento(self, pai: ctk.CTkFrame) -> None:
        """Aba de formatação do documento .docx."""
        pai.grid_columnconfigure(0, weight=1)
        pai.grid_rowconfigure(2, weight=1)

        self._montar_area_arquivo(pai, linha=0)
        self._montar_acoes(pai, linha=1)
        self._montar_log(pai, linha=2)

    def _montar_area_arquivo(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Área de seleção do arquivo .docx (botão + arrastar-e-soltar)."""
        area = ctk.CTkFrame(pai)
        area.grid(row=linha, column=0, sticky="ew", pady=(0, 10))
        area.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(area, text="Documento", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(12, 6)
        )

        self.rotulo_arquivo = ctk.CTkLabel(
            area, text="Nenhum arquivo selecionado", anchor="w", text_color="gray"
        )
        self.rotulo_arquivo.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 12))

        self.botao_selecionar = ctk.CTkButton(
            area, text="Selecionar .docx", width=150, command=self._selecionar_arquivo
        )
        self.botao_selecionar.grid(row=1, column=1, padx=15, pady=(0, 12))

        if _DND_DISPONIVEL:
            ctk.CTkLabel(
                area,
                text="Dica: arraste um arquivo .docx para esta janela",
                text_color="gray",
                font=ctk.CTkFont(size=12),
            ).grid(row=2, column=0, columnspan=2, pady=(0, 12))

    def _montar_acoes(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Botão principal, barra de progresso e botão de pasta."""
        acoes = ctk.CTkFrame(pai, fg_color="transparent")
        acoes.grid(row=linha, column=0, sticky="ew", pady=(4, 10))
        acoes.grid_columnconfigure(0, weight=1)

        self.botao_formatar = ctk.CTkButton(
            acoes,
            text="Formatar para ABNT",
            height=52,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=CORES["azul"],
            hover_color=CORES["azul_hover"],
            command=self._iniciar_formatacao,
        )
        self.botao_formatar.grid(row=0, column=0, sticky="ew")

        self.botao_pasta = ctk.CTkButton(
            acoes,
            text="Abrir pasta de destino",
            height=52,
            width=200,
            fg_color=CORES["verde"],
            hover_color=CORES["verde_hover"],
            command=self._abrir_pasta_destino,
            state="disabled",
        )
        self.botao_pasta.grid(row=0, column=1, padx=(10, 0))

        self.barra_progresso = ctk.CTkProgressBar(acoes, mode="indeterminate")
        self.barra_progresso.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.barra_progresso.set(0)

    def _montar_log(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Área de log de status."""
        self.caixa_log = ctk.CTkTextbox(pai, font=ctk.CTkFont(size=13))
        self.caixa_log.grid(row=linha, column=0, sticky="nsew")
        self.caixa_log.configure(state="disabled")
        self._registrar_log("Pronto. Selecione um arquivo .docx para começar.")

    # ── Aba: Referências ABNT ───────────────────────────────────────────────

    def _montar_aba_referencias(self, pai: ctk.CTkFrame) -> None:
        """Aba do gerador de referências (NBR 6023)."""
        pai.grid_columnconfigure(0, weight=1)
        pai.grid_rowconfigure(3, weight=1)

        self.seletor_tipo = ctk.CTkSegmentedButton(
            pai,
            values=["Livro", "Artigo", "Site", "Texto bruto"],
            command=self._trocar_tipo_referencia,
        )
        self.seletor_tipo.set("Livro")
        self.seletor_tipo.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 10))

        self.moldura_campos = ctk.CTkScrollableFrame(pai, height=210)
        self.moldura_campos.grid(row=1, column=0, sticky="ew", padx=10)
        self.moldura_campos.grid_columnconfigure(1, weight=1)
        self._construir_campos("Livro")

        self._montar_previa(pai, linha=2)
        self._montar_lista_preparo(pai, linha=3)
        self._montar_botoes_referencia(pai, linha=4)

    def _montar_previa(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Área de prévia da referência gerada."""
        moldura = ctk.CTkFrame(pai)
        moldura.grid(row=linha, column=0, sticky="nsew", padx=10, pady=10)
        moldura.grid_columnconfigure(0, weight=1)
        moldura.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            moldura, text="Prévia da referência", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            moldura,
            text="Os trechos entre ** são aplicados em negrito ao inserir no Word.",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, sticky="w", padx=10)

        self.previa = ctk.CTkTextbox(moldura, height=80, wrap="word")
        self.previa.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 10))

    def _montar_lista_preparo(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Lista das referências em preparo, antes de gravar no Word."""
        moldura = ctk.CTkFrame(pai)
        moldura.grid(row=linha, column=0, sticky="nsew", padx=10, pady=(0, 10))
        moldura.grid_columnconfigure(0, weight=1)
        moldura.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            moldura,
            text="Referências em preparo",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            moldura,
            text="Adicione quantas quiser e insira todas de uma vez no documento.",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, sticky="w", padx=10)

        self.lista_preparo = ctk.CTkTextbox(moldura, height=110, wrap="word")
        self.lista_preparo.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 4))
        self.lista_preparo.configure(state="disabled")

        controles = ctk.CTkFrame(moldura, fg_color="transparent")
        controles.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        controles.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            controles,
            text="Remover a última",
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._remover_ultima_referencia,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            controles,
            text="Limpar lista",
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._limpar_lista_preparo,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _montar_botoes_referencia(self, pai: ctk.CTkFrame, linha: int) -> None:
        """Botões de ação da aba de referências."""
        botoes = ctk.CTkFrame(pai, fg_color="transparent")
        botoes.grid(row=linha, column=0, sticky="ew", padx=10, pady=(0, 10))
        for coluna in range(4):
            botoes.grid_columnconfigure(coluna, weight=1)

        ctk.CTkButton(
            botoes, text="Gerar Referência", command=self._gerar_referencia
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            botoes,
            text="Adicionar à Lista",
            fg_color=CORES["azul"],
            hover_color=CORES["azul_hover"],
            command=self._adicionar_a_lista,
        ).grid(row=0, column=1, sticky="ew", padx=4)

        ctk.CTkButton(
            botoes,
            text="Copiar texto",
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._gerar_e_copiar,
        ).grid(row=0, column=2, sticky="ew", padx=4)

        ctk.CTkButton(
            botoes,
            text="Inserir só esta no Word",
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._inserir_no_word,
        ).grid(row=0, column=3, sticky="ew", padx=(4, 0))

        ctk.CTkButton(
            pai,
            text="Inserir Referências em Preparo no Documento Word",
            fg_color=CORES["verde"],
            hover_color=CORES["verde_hover"],
            command=self._inserir_lista_no_word,
        ).grid(row=linha + 1, column=0, sticky="ew", padx=10, pady=(0, 6))

        ctk.CTkButton(
            pai,
            text="Reformatar, realçar o negrito e ordenar as referências de um .docx",
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._ordenar_docx,
        ).grid(row=linha + 2, column=0, sticky="ew", padx=10, pady=(0, 12))

    # ── Formulário de referências ───────────────────────────────────────────

    def _trocar_tipo_referencia(self, tipo: str) -> None:
        """Reconstrói o formulário conforme o tipo escolhido."""
        self._construir_campos(tipo)
        self._limpar_previa()

    def _construir_campos(self, tipo: str) -> None:
        """Cria os campos do formulário do tipo informado."""
        for widget in self.moldura_campos.winfo_children():
            widget.destroy()
        self.campos_referencia = {}
        self.campo_autor = None
        self.rotulo_autores = None

        for indice, (chave, rotulo) in enumerate(CAMPOS_POR_TIPO.get(tipo, [])):
            ctk.CTkLabel(self.moldura_campos, text=rotulo, anchor="w").grid(
                row=indice, column=0, sticky="nw", padx=(8, 10), pady=4
            )
            if chave == "bruto":
                widget: ctk.CTkBaseClass = ctk.CTkTextbox(
                    self.moldura_campos, height=90, wrap="word"
                )
                widget.grid(row=indice, column=1, sticky="ew", padx=(0, 8), pady=4)
                self.campos_referencia[chave] = widget
            elif chave == CHAVE_AUTORES:
                self.campos_referencia[chave] = self._construir_campo_autores(
                    indice, rotulo
                )
            else:
                widget = ctk.CTkEntry(self.moldura_campos, placeholder_text=rotulo)
                widget.grid(row=indice, column=1, sticky="ew", padx=(0, 8), pady=4)
                self.campos_referencia[chave] = widget

    def _construir_campo_autores(self, linha: int, rotulo: str) -> ctk.CTkEntry:
        """Cria o seletor de vários autores: entrada + Adicionar + resumo."""
        moldura = ctk.CTkFrame(self.moldura_campos, fg_color="transparent")
        moldura.grid(row=linha, column=1, sticky="ew", padx=(0, 8), pady=4)
        moldura.grid_columnconfigure(0, weight=1)

        entrada = ctk.CTkEntry(moldura, placeholder_text=rotulo)
        entrada.grid(row=0, column=0, sticky="ew")
        entrada.bind("<Return>", lambda _evento: self._adicionar_autor())

        ctk.CTkButton(moldura, text="Adicionar", width=90, command=self._adicionar_autor).grid(
            row=0, column=1, padx=(5, 0)
        )

        self.rotulo_autores = ctk.CTkLabel(
            moldura,
            text="Nenhum autor adicionado",
            anchor="w",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        )
        self.rotulo_autores.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        ctk.CTkButton(
            moldura,
            text="Limpar autores",
            width=90,
            fg_color=CORES["cinza"],
            hover_color=CORES["cinza_hover"],
            command=self._limpar_autores,
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.campo_autor = entrada
        self._renderizar_autores()
        return entrada

    def _adicionar_autor(self) -> None:
        """Acrescenta o autor digitado à lista de autores."""
        if self.campo_autor is None:
            return
        nome = self.campo_autor.get().strip()
        if not nome:
            return
        self.autores.append(nome)
        self.campo_autor.delete(0, "end")
        self._renderizar_autores()

    def _limpar_autores(self) -> None:
        """Descarta todos os autores já adicionados."""
        self.autores.clear()
        if self.campo_autor is not None:
            self.campo_autor.delete(0, "end")
        self._renderizar_autores()

    def _renderizar_autores(self) -> None:
        """Resume quantos e quais autores já foram adicionados."""
        if self.rotulo_autores is None:
            return
        if not self.autores:
            self.rotulo_autores.configure(text="Nenhum autor adicionado")
            return
        self.rotulo_autores.configure(text=" • ".join(self.autores))

    def _autores_do_formulario(self) -> list[str]:
        """Junta os autores adicionados com o que ainda está digitado no campo."""
        autores = list(self.autores)
        if self.campo_autor is not None:
            digitado = self.campo_autor.get().strip()
            if digitado:
                autores.append(digitado)
        return autores

    def _ler_campo(self, chave: str) -> str:
        """Lê o valor de um campo do formulário."""
        widget = self.campos_referencia.get(chave)
        if widget is None:
            return ""
        if isinstance(widget, ctk.CTkTextbox):
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def _ler_data_acesso(self) -> datetime | None:
        """Interpreta a data de acesso digitada (dd/mm/aaaa)."""
        texto = self._ler_campo("data_acesso")
        if not texto:
            return None
        for formato in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue
        return None

    def _montar_referencia(self) -> Referencia | None:
        """Constrói a referência a partir dos campos preenchidos."""
        tipo = self.seletor_tipo.get()
        autores = self._autores_do_formulario()

        if tipo == "Livro":
            return self.formatador.format_book(
                title=self._ler_campo("titulo"),
                edition=self._ler_campo("edicao"),
                city=self._ler_campo("cidade"),
                publisher=self._ler_campo("editora"),
                year=self._ler_campo("ano") or None,
                authors=autores,
            )
        if tipo == "Artigo":
            return self.formatador.format_journal_article(
                article_title=self._ler_campo("titulo_artigo"),
                journal_title=self._ler_campo("titulo_periodico"),
                city=self._ler_campo("cidade"),
                volume=self._ler_campo("volume"),
                number=self._ler_campo("numero"),
                pages=self._ler_campo("paginas"),
                year=self._ler_campo("ano") or None,
                authors=autores,
            )
        if tipo == "Site":
            return self.formatador.format_website(
                title=self._ler_campo("titulo"),
                url=self._ler_campo("url"),
                access_date=self._ler_data_acesso(),
                site_name=self._ler_campo("site_nome"),
                authors=autores,
            )

        bruto = self._ler_campo("bruto")
        if not bruto:
            return None
        return self.formatador.analisar_texto_bruto(bruto)

    def _limpar_previa(self) -> None:
        """Limpa a área de prévia e a referência em memória."""
        self.referencia_atual = None
        self.previa.delete("1.0", "end")

    def _mostrar_previa(self, referencia: Referencia) -> None:
        """Exibe a referência gerada na prévia."""
        self.previa.delete("1.0", "end")
        self.previa.insert("1.0", referencia.texto_markdown)

    def _gerar_referencia(self, avisar: bool = True) -> Referencia | None:
        """Gera a referência dos campos e atualiza a prévia."""
        referencia = self._montar_referencia()
        if referencia is None or not referencia.texto_puro.strip():
            if avisar:
                messagebox.showinfo("Atenção", "Preencha os campos da referência.")
            return None

        self.referencia_atual = referencia
        self._mostrar_previa(referencia)
        return referencia

    def _gerar_e_copiar(self) -> None:
        """Gera a referência, copia o texto simples e confirma no log."""
        referencia = self._gerar_referencia()
        if referencia is None:
            return

        self.clipboard_clear()
        self.clipboard_append(referencia.texto_puro)
        self.abas.set("Formatar Documento")
        self._registrar_log("Referência gerada e copiada para a área de transferência:")
        self._registrar_log(referencia.texto_puro)

    def _inserir_no_word(self) -> None:
        """Insere a referência na seção REFERÊNCIAS de um arquivo .docx."""
        referencia = self._gerar_referencia()
        if referencia is None:
            return

        destino = self._escolher_docx("Selecione o documento que receberá a referência")
        if destino is None:
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"Inserir a referência em “{destino.name}”?\n\nO arquivo será atualizado.",
        ):
            return

        try:
            documento = abrir(destino)
            referencias.inserir_referencia(documento, referencia)
            salvar(documento, destino)
        except Exception as erro:  # noqa: BLE001 - reportado ao usuário
            messagebox.showerror("Falha ao inserir", str(erro))
            return

        self._registrar_log(f"Referência inserida em: {destino}")
        messagebox.showinfo("Concluído", "Referência inserida e ordenada com sucesso.")

    # ── Lista de referências em preparo ─────────────────────────────────────

    def _adicionar_a_lista(self) -> None:
        """Acrescenta a referência gerada à lista em preparo."""
        referencia = self._gerar_referencia()
        if referencia is None:
            return

        self.referencias_preparadas.append(referencia)
        self._renderizar_lista_preparo()
        self._registrar_log(
            f"Referência adicionada à lista ({len(self.referencias_preparadas)} no total)."
        )

    def _remover_ultima_referencia(self) -> None:
        """Remove a última referência da lista em preparo."""
        if not self.referencias_preparadas:
            return
        self.referencias_preparadas.pop()
        self._renderizar_lista_preparo()

    def _limpar_lista_preparo(self) -> None:
        """Esvazia a lista de referências em preparo."""
        self.referencias_preparadas.clear()
        self._renderizar_lista_preparo()

    def _renderizar_lista_preparo(self) -> None:
        """Mostra a lista em preparo, numerada na ordem de cadastro."""
        self.lista_preparo.configure(state="normal")
        self.lista_preparo.delete("1.0", "end")

        if not self.referencias_preparadas:
            self.lista_preparo.insert("1.0", "Nenhuma referência em preparo.")
        else:
            for indice, referencia in enumerate(self.referencias_preparadas, start=1):
                self.lista_preparo.insert(
                    "end", f"{indice}. {referencia.texto_markdown}\n\n"
                )

        self.lista_preparo.configure(state="disabled")

    def _inserir_lista_no_word(self) -> None:
        """Insere todas as referências em preparo na seção REFERÊNCIAS do Word."""
        if not self.referencias_preparadas:
            messagebox.showinfo(
                "Lista vazia",
                "Adicione ao menos uma referência à lista em preparo.",
            )
            return

        destino = self._escolher_docx("Selecione o documento que receberá as referências")
        if destino is None:
            return

        quantidade = len(self.referencias_preparadas)
        if not messagebox.askyesno(
            "Confirmar",
            f"Inserir {quantidade} referência(s) em “{destino.name}”?\n\n"
            "O arquivo será atualizado.",
        ):
            return

        try:
            documento = abrir(destino)
            total = referencias.inserir_referencias(documento, self.referencias_preparadas)
            salvar(documento, destino)
        except Exception as erro:  # noqa: BLE001 - reportado ao usuário
            messagebox.showerror("Falha ao inserir", str(erro))
            return

        self.abas.set("Formatar Documento")
        self._registrar_log(
            f"{total} referência(s) inserida(s) e ordenada(s) em: {destino}"
        )
        messagebox.showinfo(
            "Concluído",
            f"{total} referência(s) inserida(s) e ordenadas com sucesso.",
        )

    def _ordenar_docx(self) -> None:
        """Reformata, reaplica o negrito e ordena as referências de um .docx."""
        destino = self._escolher_docx("Selecione o documento com referências")
        if destino is None:
            return

        try:
            documento = abrir(destino)
            total = referencias.formatar_secao_referencias(documento)
            if total == 0:
                messagebox.showinfo(
                    "Nada a ordenar",
                    "Não foi encontrada uma seção REFERÊNCIAS com itens neste documento.",
                )
                return
            salvar(documento, destino)
        except Exception as erro:  # noqa: BLE001 - reportado ao usuário
            messagebox.showerror("Falha ao ordenar", str(erro))
            return

        self.abas.set("Formatar Documento")
        self._registrar_log(
            f"{total} referência(s) reformatada(s), com negrito realçado e "
            f"ordenadas em: {destino}"
        )
        messagebox.showinfo(
            "Concluído",
            f"{total} referência(s) reformatada(s), com o negrito realçado e "
            "ordenadas com sucesso.",
        )

    def _escolher_docx(self, titulo: str) -> Path | None:
        """Abre o diálogo de seleção de um .docx de destino."""
        caminho = filedialog.askopenfilename(
            title=titulo,
            filetypes=[("Documentos Word", "*.docx")],
            initialdir=self.preferencias.ultima_pasta or None,
        )
        if not caminho:
            return None

        escolhido = Path(caminho)
        self.preferencias.ultima_pasta = str(escolhido.parent)
        salvar_preferencias(self.preferencias)
        return escolhido

    # ── Drag and drop ───────────────────────────────────────────────────────

    def _configurar_drag_and_drop(self) -> None:
        """Registra a janela como alvo de arrastar-e-soltar, quando disponível."""
        if not _DND_DISPONIVEL:
            return
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._ao_soltar_arquivo)
        except Exception:  # pragma: no cover - depende do ambiente
            pass

    def _ao_soltar_arquivo(self, evento) -> None:
        """Trata o arquivo solto na janela."""
        caminho = str(evento.data).strip().strip("{}").strip('"')
        self.abas.set("Formatar Documento")
        self._definir_arquivo(Path(caminho))

    # ── Formatação do documento ─────────────────────────────────────────────

    def _selecionar_arquivo(self) -> None:
        """Abre o diálogo de seleção de arquivo."""
        caminho = filedialog.askopenfilename(
            title="Selecione um documento Word",
            filetypes=[("Documentos Word", "*.docx")],
            initialdir=self.preferencias.ultima_pasta or None,
        )
        if caminho:
            self._definir_arquivo(Path(caminho))

    def _definir_arquivo(self, caminho: Path) -> None:
        """Define o arquivo de entrada escolhido."""
        if caminho.suffix.lower() != ".docx":
            messagebox.showwarning(
                "Formato inválido", "Selecione um arquivo no formato .docx."
            )
            return

        self.arquivo_entrada = caminho
        self.rotulo_arquivo.configure(text=str(caminho), text_color=("black", "white"))
        self.preferencias.ultima_pasta = str(caminho.parent)
        salvar_preferencias(self.preferencias)
        self._registrar_log(f"Arquivo selecionado: {caminho.name}")

    def _iniciar_formatacao(self) -> None:
        """Valida a entrada e dispara a formatação em segundo plano."""
        if self.arquivo_entrada is None:
            messagebox.showinfo("Atenção", "Selecione um arquivo .docx primeiro.")
            return

        self._bloquear_controles(True)
        self.barra_progresso.start()
        self._registrar_log("-" * 40)
        threading.Thread(target=self._executar_formatacao, daemon=True).start()

    def _executar_formatacao(self) -> None:
        """Executa o motor ABNT (roda em thread separada)."""
        try:
            normas = NormasABNT(
                fonte_corpo=self.preferencias.fonte,
                fonte_titulo=self.preferencias.fonte,
            )
            motor = MotorABNT(normas)
            resultado = motor.processar(
                self.arquivo_entrada,
                progresso=lambda msg: self.after(0, self._registrar_log, msg),
            )
        except Exception as erro:  # noqa: BLE001 - reportado ao usuário
            self.after(0, self._ao_falhar, erro)
            return
        self.after(0, self._finalizar, resultado)

    def _finalizar(self, resultado: ResultadoFormatacao) -> None:
        """Atualiza a interface ao concluir com sucesso."""
        self.ultimo_resultado = resultado
        self.barra_progresso.stop()
        self.barra_progresso.set(1)
        self._bloquear_controles(False)
        self.botao_pasta.configure(state="normal")

        self._registrar_log(
            f"Títulos: {resultado.titulos_aplicados} | "
            f"Citações longas: {resultado.citacoes_aplicadas} | "
            f"Parágrafos: {resultado.paragrafos_formatados} | "
            f"Referências: {resultado.referencias_ordenadas}"
        )
        self._registrar_log(f"Arquivo gerado: {resultado.arquivo_saida}")
        self._registrar_log("Concluído com sucesso!")

        try:
            historico.registrar(self.arquivo_entrada, resultado.arquivo_saida, "concluido")
        except Exception:  # pragma: no cover - histórico não deve travar a GUI
            pass

    def _ao_falhar(self, erro: Exception) -> None:
        """Atualiza a interface quando ocorre um erro."""
        self.barra_progresso.stop()
        self.barra_progresso.set(0)
        self._bloquear_controles(False)
        self._registrar_log(f"Erro: {erro}")
        messagebox.showerror("Falha na formatação", str(erro))

    def _abrir_pasta_destino(self) -> None:
        """Abre no explorador a pasta do arquivo gerado."""
        if self.ultimo_resultado is None:
            return
        abrir_pasta(self.ultimo_resultado.arquivo_saida.parent)

    def _alternar_tema(self) -> None:
        """Alterna entre tema claro e escuro, salvando a preferência."""
        novo = "light" if ctk.get_appearance_mode().lower() == "dark" else "dark"
        ctk.set_appearance_mode(novo)
        self.preferencias.tema = novo
        salvar_preferencias(self.preferencias)

    # ── Utilidades ──────────────────────────────────────────────────────────

    def _registrar_log(self, mensagem: str) -> None:
        """Acrescenta uma linha ao log visual."""
        self.caixa_log.configure(state="normal")
        self.caixa_log.insert("end", f"{mensagem}\n")
        self.caixa_log.see("end")
        self.caixa_log.configure(state="disabled")

    def _bloquear_controles(self, bloqueado: bool) -> None:
        """Habilita ou desabilita os botões durante o processamento."""
        estado = "disabled" if bloqueado else "normal"
        self.botao_formatar.configure(state=estado)
        self.botao_selecionar.configure(state=estado)


def abrir_pasta(caminho: Path) -> None:
    """Abre a pasta informada no gerenciador de arquivos do sistema."""
    if sys.platform.startswith("win"):
        os.startfile(caminho)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(caminho)], check=False)
    else:
        subprocess.run(["xdg-open", str(caminho)], check=False)


def nome_sugerido(entrada: Path) -> Path:
    """Nome de saída sugerido para o arquivo formatado."""
    return nome_saida_padrao(entrada)


def main() -> None:
    """Ponto de entrada da aplicação gráfica."""
    aplicacao = AplicacaoABNT()
    aplicacao.mainloop()


if __name__ == "__main__":
    main()
