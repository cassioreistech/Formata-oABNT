# Formata-oABNT

Aplicação **desktop** (Windows) que formata documentos Word `.docx` nas normas
ABNT. Roda 100% local, sem internet, sem servidor e sem Docker.

## Funcionalidades

- **NBR 14724** — papel A4, margens (3 cm superior/esquerda, 2 cm inferior/direita),
  Arial ou Times New Roman 12 pt, espaçamento 1,5, texto justificado, recuo de 1,25 cm.
- **NBR 10520** — aplica o estilo `ABNT_CitacaoLonga` (recuo 4 cm, 10 pt, espaço simples)
  a citações diretas com mais de 3 linhas.
- **NBR 6024** — identifica a hierarquia de títulos (`1. INTRODUÇÃO`, `1.1 Objetivos`).
- **NBR 6023** — gerador de referências (livro, artigo de periódico e site), com
  destaque em negrito real, **reanálise automática do negrito** em referências já
  existentes e ordenação alfabética automática na seção REFERÊNCIAS.
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

## Uso — Aba "Referências ABNT"

1. Escolha o tipo: **Livro**, **Artigo**, **Site** ou **Texto bruto**.
2. Preencha os campos (ou cole a referência já escrita na opção "Texto bruto").
3. **Gerar Referência** mostra a prévia; **Gerar e Copiar Referência** envia o texto
   para a área de transferência.
4. **Inserir na Seção de Referências do Word** insere o item em um `.docx`,
   criando a seção `REFERÊNCIAS` se necessário.
5. **Reformatar, realçar o negrito e ordenar as referências de um .docx** analisa
   cada referência já escrita, **reaplica o negrito no trecho correto** (título do
   livro, título do periódico ou primeira palavra do site sem autor) e reorganiza
   a seção inteira em ordem alfabética. O texto não é alterado: apenas o destaque
   em negrito é reposicionado.

> O motor de formatação também executa essa reanálise automaticamente ao processar
> o documento — a seção REFERÊNCIAS sai corrigida, realçada e ordenada.

## Uso — Como biblioteca

```python
from abnt_engine import formatar_para_abnt
from abnt_references import ABNTReferenceFormatter

resultado = formatar_para_abnt(
    "meu_tcc.docx",
    progresso=lambda msg: print(msg),
)
print("Gerado em:", resultado.arquivo_saida)

formatador = ABNTReferenceFormatter()
livro = formatador.format_book(
    author="Maria Helena Diniz",
    title="Curso de Direito Civil Brasileiro",
    edition="38",
    city="São Paulo",
    publisher="Saraiva",
    year=2022,
)
print(livro.texto_puro)      # texto simples
print(livro.texto_markdown)  # com os destaques em **negrito**
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
├── abnt_references.py    # Formatação de referências (NBR 6023)
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
│   ├── referencias.py    # Seção REFERÊNCIAS: inserir, realçar e ordenar (NBR 6023)
│   ├── sanitizador.py    # Limpeza de artefatos de cópia
│   ├── docx_io.py        # Abrir/salvar .docx
│   ├── caminhos.py       # Nomes de arquivo de saída
│   ├── config.py         # Preferências (JSON)
│   └── historico.py      # Histórico (SQLite)
└── tests/                # Testes pytest por módulo
```
