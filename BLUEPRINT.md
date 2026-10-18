# Formata-oABNT — Blueprint do Projeto

## Visão Geral

Sistema premium de formatação automática de documentos acadêmicos conforme as normas ABNT.
Gera arquivos **DOCX** (principal) e **PDF** (secundário) com formatação precisa.

---

## Normas ABNT Cobertas

| Norma | Descrição |
|-------|-----------|
| NBR 14724 | Trabalhos acadêmicos (estrutura, margens, fonte, espaçamento) |
| NBR 6023 | Referências bibliográficas |
| NBR 6024 | Numeração progressiva das seções |
| NBR 6027 | Sumário |
| NBR 6028 | Resumo e palavras-chave |
| NBR 10520 | Citações no texto |
| NBR 15287 | Projetos de pesquisa |
| NBR 14724:2024 | Atualização recente (verificar alterações) |

---

## Tipos de Documento Suportados

1. **TCC / Monografia** — Graduação
2. **Artigo Científico** — Periódicos e conferências
3. **Dissertação** — Mestrado
4. **Tese** — Doutorado
5. **Relatório Técnico** — Projeto, estágio, pesquisa
6. **Projeto de Pesquisa** — NBR 15287

---

## Arquitetura

```
Formata-oABNT/
├── src/
│   ├── core/                    # Núcleo do sistema
│   │   ├── __init__.py
│   │   ├── engine.py            # Motor principal de formatação
│   │   ├── models.py            # Modelos de dados (documento, seção, referência)
│   │   ├── config.py            # Configurações e constantes ABNT
│   │   └── exceptions.py        # Exceções customizadas
│   │
│   ├── formatters/              # Formatadores por tipo de documento
│   │   ├── __init__.py
│   │   ├── base.py              # Classe base abstrata
│   │   ├── tcc.py               # TCC / Monografia
│   │   ├── artigo.py            # Artigo científico
│   │   ├── dissertacao.py       # Dissertação
│   │   ├── tese.py              # Tese
│   │   ├── relatorio.py         # Relatório técnico
│   │   └── projeto_pesquisa.py  # Projeto de pesquisa
│   │
│   ├── generators/              # Geradores de saída
│   │   ├── __init__.py
│   │   ├── docx_generator.py    # Geração DOCX (python-docx)
│   │   ├── pdf_generator.py     # Conversão para PDF
│   │   └── styles.py            # Estilos ABNT definidos
│   │
│   ├── parsers/                 # Parsers de entrada
│   │   ├── __init__.py
│   │   ├── markdown_parser.py   # Entrada em Markdown
│   │   ├── json_parser.py       # Entrada em JSON/YAML
│   │   └── text_parser.py       # Entrada em texto simples
│   │
│   ├── validators/              # Validadores ABNT
│   │   ├── __init__.py
│   │   ├── structure.py         # Validação de estrutura
│   │   ├── references.py        # Validação de referências
│   │   ├── citations.py         # Validação de citações
│   │   └── formatting.py        # Validação de formatação
│   │
│   └── cli/                     # Interface de linha de comando
│       ├── __init__.py
│       ├── app.py               # CLI principal
│       └── commands.py          # Comandos disponíveis
│
├── templates/                   # Templates de documentos
│   ├── tcc/
│   ├── artigo/
│   ├── dissertacao/
│   ├── tese/
│   ├── relatorio/
│   └── projeto_pesquisa/
│
├── examples/                    # Exemplos de uso
│   ├── exemplo_tcc.json
│   ├── exemplo_artigo.md
│   └── exemplo_simples.yaml
│
├── tests/                       # Testes
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                        # Documentação
│   ├── uso.md
│   ├── api.md
│   └── normas.md
│
├── pyproject.toml               # Configuração do projeto
├── requirements.txt             # Dependências
├── README.md                    # Documentação principal
└── .gitignore
```

---

## Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| Linguagem | Python 3.11+ |
| Geração DOCX | python-docx |
| Geração PDF | docx2pdf / LibreOffice headless |
| CLI | Click ou Typer |
| Validação | Pydantic |
| Testes | pytest |
| Lint | Ruff |
| Formatação | Black |
| Banco (futuro) | PostgreSQL + SQLAlchemy |

---

## Dependências Principais

```
python-docx>=1.1.0
pydantic>=2.0
typer>=0.9.0
rich>=13.0
docx2pdf>=0.1.8
pyyaml>=6.0
```

---

## Módulos Detalhados

### 1. Core Engine (`core/engine.py`)
- Recebe dados do documento (título, autor, seções, referências, etc.)
- Aplica regras ABNT conforme o tipo de documento
- Orquestra a geração da saída

### 2. Formatters (`formatters/`)
- Cada tipo de documento tem seu formatter
- Define estrutura obrigatória (elementos pré-textuais, textuais, pós-textuais)
- Aplica regras específicas (ex: TCC precisa de folha de aprovação)

### 3. Generators (`generators/`)
- `docx_generator.py`: Cria o documento .docx com:
  - Margens (esq/sup: 3cm, dir/inf: 2cm)
  - Fonte Arial ou Times New Roman, 12pt
  - Espaçamento 1.5 entre linhas
  - Numeração de páginas
  - Cabeçalhos/seções
  - Estilos para títulos, corpo, citações longas
- `pdf_generator.py`: Converte DOCX → PDF

### 4. Validators (`validators/`)
- Verifica se o documento atende às normas antes de gerar
- Retorna lista de erros/avisos com referência à norma

### 5. CLI (`cli/`)
- `formatar`: Gera o documento
- `validar`: Apenas valida sem gerar
- `modelo`: Gera template/modelo para preenchimento
- `info`: Mostra informações sobre normas

---

## Fluxo de Uso

```
Usuário fornece dados (JSON/YAML/Markdown/interativo)
    ↓
Parser converte para modelo interno
    ↓
Formatter aplica regras ABNT do tipo de documento
    ↓
Validator verifica conformidade
    ↓
Generator cria DOCX (e opcionalmente PDF)
    ↓
Arquivo final entregue ao usuário
```

---

## Fases de Implementação

### Fase 1 — Fundação (atual)
- [x] Estrutura do projeto
- [ ] Core engine + models
- [ ] Configurações ABNT
- [ ] Gerador DOCX básico
- [ ] Formatter para TCC

### Fase 2 — Expansão
- [ ] Todos os formatters
- [ ] Gerador PDF
- [ ] Validadores
- [ ] CLI completo

### Fase 3 — Premium
- [ ] Templates visuais customizáveis
- [ ] Validação inteligente com sugestões
- [ ] Importação de bibliografias (BibTeX, RIS)
- [ ] Preview visual antes de gerar

### Fase 4 — Nuvem
- [ ] API FastAPI
- [ ] Frontend web
- [ ] PostgreSQL para histórico
- [ ] Autenticação e planos