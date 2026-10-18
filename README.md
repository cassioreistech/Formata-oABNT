# Formata-oABNT

Lê um arquivo `.docx` existente, reaplica a formatação da **NBR 14724**
(margens, fonte, espaçamento, alinhamento e títulos) e salva o resultado.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
```

## Uso pela linha de comando

```bash
# Gera <entrada>_abnt.docx
formata-abnt meu_tcc.docx

# Escolhendo o arquivo de saída e a fonte
formata-abnt meu_tcc.docx -o meu_tcc_formatado.docx --fonte Arial
```

## Uso como biblioteca

```python
from formata_abnt.abnt.reformatador import ReformatadorABNT
from formata_abnt.docx_io import abrir, salvar

documento = abrir("meu_tcc.docx")
ReformatadorABNT().reformatar(documento)
salvar(documento, "meu_tcc_abnt.docx")
```

## Regras aplicadas (NBR 14724)

| Item | Valor |
|------|-------|
| Margens | 3 cm (superior/esquerda), 2 cm (inferior/direita) |
| Fonte | Times New Roman 12 pt |
| Espaçamento entre linhas | 1,5 |
| Alinhamento do corpo | Justificado |
| Recuo da 1ª linha | 1,25 cm |
| Títulos nível 1 | Centralizado, negrito, sem recuo |

Os valores são configuráveis via `NormasABNT` (ex.: trocar a fonte para Arial).

## Testes

```bash
python -m pytest -q
```

## Estrutura

```
formata_abnt/
├── abnt/
│   ├── normas.py        # parâmetros da NBR 14724
│   ├── runs.py          # aplica fonte a um run
│   ├── margens.py       # margens das seções
│   ├── fontes.py        # fonte/tamanho do corpo
│   ├── paragrafos.py    # espaçamento, recuo e justificação
│   ├── titulos.py       # detecção e formatação de títulos
│   └── reformatador.py  # orquestra tudo
├── docx_io.py           # abrir/salvar .docx
└── cli.py               # linha de comando
```
