# Formata-oABNT

Aplicação **desktop** (Windows) que formata documentos Word `.docx` nas normas
ABNT. Roda 100% local, sem internet, sem servidor e sem Docker.

## Funcionalidades

- **NBR 14724** — papel A4, margens (3 cm superior/esquerda, 2 cm inferior/direita),
  Arial ou Times New Roman 12 pt, espaçamento 1,5, texto justificado, recuo de 1,25 cm.
- **NBR 10520** — aplica o estilo `ABNT_CitacaoLonga` (recuo 4 cm, 10 pt, espaço simples)
  a citações diretas com mais de 3 linhas.
- **NBR 6024** — identifica a hierarquia de títulos (`1. INTRODUÇÃO`, `1.1 Objetivos`).
- **Sanitização** — remove espaços invisíveis, espaços repetidos, quebras duplas e
  artefatos de cópia da web/PDF.
- **Preservação de marcações** — negrito, itálico e sublinhado do texto são mantidos.
- **Histórico** — registros em SQLite local; preferências em JSON.

## Requisitos

- Python 3.11+ (testado com 3.15)
- Windows, macOS ou Linux (empacotamento `.exe` focado no Windows)

## Instalação (desenvolvimento)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -e ".[dev,build]"
```

## Uso — Interface gráfica

```bash
python app_gui.py
```

1. Selecione ou **arraste** um `.docx` para a janela.
2. Clique em **Formatar para ABNT**.
3. Acompanhe o log e o progresso.
4. Use **Abrir pasta de destino** para localizar o arquivo `*_abnt.docx`.

## Uso — Como biblioteca

```python
from abnt_engine import formatar_para_abnt

resultado = formatar_para_abnt(
    "meu_tcc.docx",
    progresso=lambda msg: print(msg),
)
print("Gerado em:", resultado.arquivo_saida)
```

## Gerar o executável (.exe)

```bash
python build_exe.py            # arquivo único
python build_exe.py --onedir   # pasta
```

O executável é criado em `dist/FormataABNT.exe` e roda no Windows sem Python instalado.

## Testes

```bash
python -m pytest -q
```

## Estrutura

```
Formata-oABNT/
├── abnt_engine.py        # Motor ABNT (pipeline completo)
├── app_gui.py            # Interface gráfica (CustomTkinter)
├── build_exe.py          # Empacotamento com PyInstaller
├── formata_abnt/
│   ├── normas.py         # Parâmetros das normas ABNT
│   ├── margens.py        # Papel A4 e margens
│   ├── tipografia.py     # Fonte, espaçamento, recuo e justificação
│   ├── runs.py           # Aplicação de fonte em runs
│   ├── titulos.py        # Hierarquia de títulos (NBR 6024)
│   ├── estilos.py        # Estilo ABNT_CitacaoLonga
│   ├── citacao_longa.py  # Detecção de citações longas (NBR 10520)
│   ├── sanitizador.py    # Limpeza de artefatos de cópia
│   ├── docx_io.py        # Abrir/salvar .docx
│   ├── caminhos.py       # Nomes de arquivo de saída
│   ├── config.py         # Preferências (JSON)
│   └── historico.py      # Histórico (SQLite)
└── tests/                # Testes pytest por módulo
```
