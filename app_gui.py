"""Interface gráfica (CustomTkinter) do Formata-oABNT.

Janela com seleção/arrastar de arquivo, botão de formatação, barra de
progresso, log de status e atalho para abrir a pasta de destino.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from abnt_engine import MotorABNT, ResultadoFormatacao
from formata_abnt import historico
from formata_abnt.caminhos import nome_saida_padrao
from formata_abnt.config import Preferencias, carregar_preferencias, salvar_preferencias
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
}


class AplicacaoABNT(_JanelaBase):
    """Janela principal da aplicação de formatação ABNT."""

    def __init__(self) -> None:
        super().__init__()

        self.preferencias: Preferencias = carregar_preferencias()
        self.arquivo_entrada: Path | None = None
        self.ultimo_resultado: ResultadoFormatacao | None = None

        self.title("Formata-oABNT — Formatador de Documentos")
        self.geometry("760x640")
        self.minsize(680, 560)
        ctk.set_appearance_mode(self.preferencias.tema)

        self._montar_interface()
        self._configurar_drag_and_drop()

    # ── Interface ───────────────────────────────────────────────────────────

    def _montar_interface(self) -> None:
        """Constrói os widgets da janela."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._montar_cabecalho()
        self._montar_area_arquivo()
        self._montar_acoes()
        self._montar_log()

    def _montar_cabecalho(self) -> None:
        """Cabeçalho com título e alternador de tema."""
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        cabecalho.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            cabecalho,
            text="Formata-oABNT",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        titulo.grid(row=0, column=0, sticky="w")

        subtitulo = ctk.CTkLabel(
            cabecalho,
            text="Formatação de documentos Word nas normas ABNT",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        subtitulo.grid(row=1, column=0, sticky="w")

        self.botao_tema = ctk.CTkButton(
            cabecalho,
            text="Tema",
            width=80,
            command=self._alternar_tema,
            fg_color="transparent",
            border_width=1,
        )
        self.botao_tema.grid(row=0, column=1, rowspan=2, sticky="e")

    def _montar_area_arquivo(self) -> None:
        """Área de seleção do arquivo .docx (botão + arrastar-e-soltar)."""
        area = ctk.CTkFrame(self)
        area.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        area.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            area, text="Documento", font=ctk.CTkFont(size=14, weight="bold")
        )
        titulo.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 6))

        self.rotulo_arquivo = ctk.CTkLabel(
            area,
            text="Nenhum arquivo selecionado",
            anchor="w",
            text_color="gray",
        )
        self.rotulo_arquivo.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 12))

        self.botao_selecionar = ctk.CTkButton(
            area,
            text="Selecionar .docx",
            width=150,
            command=self._selecionar_arquivo,
        )
        self.botao_selecionar.grid(row=1, column=1, padx=15, pady=(0, 12))

        dica = "Arraste um arquivo .docx para esta janela" if _DND_DISPONIVEL else ""
        if dica:
            ctk.CTkLabel(area, text=dica, text_color="gray", font=ctk.CTkFont(size=12)).grid(
                row=2, column=0, columnspan=2, pady=(0, 12)
            )

    def _montar_acoes(self) -> None:
        """Botão principal de formatação, barra de progresso e botão de pasta."""
        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.grid(row=2, column=0, sticky="ew", padx=20, pady=(4, 10))
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

    def _montar_log(self) -> None:
        """Área de log de status."""
        self.caixa_log = ctk.CTkTextbox(self, font=ctk.CTkFont(size=13))
        self.caixa_log.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.caixa_log.configure(state="disabled")
        self._registrar_log("Pronto. Selecione um arquivo .docx para começar.")

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
        self._definir_arquivo(Path(caminho))

    # ── Ações ───────────────────────────────────────────────────────────────

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
        thread = threading.Thread(target=self._executar_formatacao, daemon=True)
        thread.start()

    def _executar_formatacao(self) -> None:
        """Executa o motor ABNT (roda em thread separada)."""
        try:
            normas = NormasABNT(fonte_corpo=self.preferencias.fonte,
                                fonte_titulo=self.preferencias.fonte)
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
            f"Parágrafos: {resultado.paragrafos_formatados}"
        )
        self._registrar_log(f"Arquivo gerado: {resultado.arquivo_saida}")
        self._registrar_log("Concluído com sucesso!")

        try:
            historico.registrar(
                self.arquivo_entrada, resultado.arquivo_saida, "concluido"
            )
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
        pasta = self.ultimo_resultado.arquivo_saida.parent
        abrir_pasta(pasta)

    def _alternar_tema(self) -> None:
        """Alterna entre tema claro e escuro, salvando a preferência."""
        atual = ctk.get_appearance_mode().lower()
        novo = "light" if atual == "dark" else "dark"
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
