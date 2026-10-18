# 🎓 Formata-oABNT

Sistema premium de formatação automática de documentos acadêmicos conforme as normas ABNT.

## ✨ Funcionalidades

- **Formatação automática** conforme NBR 14724, 6023, 6024, 6027, 6028, 10520
- **Tipos de documento**: TCC, Artigo, Dissertação, Tese, Relatório, Projeto de Pesquisa
- **Saída em DOCX** (principal) e PDF
- **Validação de conformidade** antes de gerar
- **CLI interativa** com Rich
- **Modelos prontos** para preenchimento rápido

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/cassioreistech/Formata-oABNT.git
cd Formata-oABNT

# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -e ".[dev]"
```

## 📖 Uso

### Gerar modelo para preenchimento

```bash
# Gera um template JSON para TCC
formata-abnt modelo tcc

# Gera template para artigo
formata-abnt modelo artigo
```

### Formatar documento

```bash
# Formata a partir de um arquivo JSON
formata-abnt formatar meu_trabalho.json

# Especificar formato de saída
formata-abnt formatar meu_trabalho.json --formato docx

# Especificar arquivo de saída
formata-abnt formatar meu_trabalho.json --saida meu_tcc_formatado.docx
```

### Informações sobre normas

```bash
formata-abnt info
```

## 📁 Estrutura do Arquivo de Entrada

O sistema aceita arquivos **JSON** ou **YAML** com a seguinte estrutura:

```json
{
  "metadados": {
    "titulo": "Título do Trabalho",
    "autores": [{"nome_completo": "Nome do Autor"}],
    "tipo": "tcc",
    "instituicao": "Universidade",
    "cidade": "Cidade",
    "ano": 2024
  },
  "resumo": "Texto do resumo...",
  "secoes": [
    {
      "titulo": "Introdução",
      "nivel": 1,
      "conteudo": ["Parágrafo 1...", "Parágrafo 2..."]
    }
  ],
  "referencias": [
    {
      "tipo": "livro",
      "autores": ["SOBRENOME, Nome"],
      "titulo": "Título do Livro",
      "ano": 2023,
      "editora": "Editora"
    }
  ]
}
```

## 📋 Normas ABNT Cobertas

| Norma | Descrição |
|-------|-----------|
| NBR 14724 | Trabalhos acadêmicos — Estrutura e formatação |
| NBR 6023 | Referências bibliográficas |
| NBR 6024 | Numeração progressiva das seções |
| NBR 6027 | Sumário |
| NBR 6028 | Resumo e palavras-chave |
| NBR 10520 | Citações no texto |
| NBR 15287 | Projetos de pesquisa |

## 🛠️ Desenvolvimento

```bash
# Rodar testes
pytest

# Lint
ruff check .

# Formatação
ruff format .
```

## 📄 Licença

MIT License