"""Testes da formatação de referências (ABNT NBR 6023)."""

from __future__ import annotations

from datetime import datetime

from abnt_references import (
    ABNTReferenceFormatter,
    MESES_ABNT,
    Referencia,
    Segmento,
    ajustar_intervalo,
    normalizar_para_ordenacao,
)

FORMATADOR = ABNTReferenceFormatter()


def test_format_author_name_inverte_sobrenome() -> None:
    """'João da Silva' vira 'SILVA, João da'."""
    assert FORMATADOR.format_author_name("João da Silva") == "SILVA, João da"
    assert FORMATADOR.format_author_name("  Maria   Helena Diniz ") == "DINIZ, Maria Helena"
    assert FORMATADOR.format_author_name("Platão") == "PLATÃO"
    assert FORMATADOR.format_author_name("") == ""


def test_format_author_name_aceita_ja_invertido() -> None:
    """Um autor já invertido só garante a caixa alta do sobrenome."""
    assert FORMATADOR.format_author_name("silva, João da") == "SILVA, João da"


def test_format_book() -> None:
    """Livro: autor invertido, título em negrito, imprenta no fim."""
    referencia = FORMATADOR.format_book(
        author="Maria Helena Diniz",
        title="Curso de Direito Civil Brasileiro",
        edition="38",
        city="São Paulo",
        publisher="Saraiva",
        year=2022,
    )

    assert referencia.tipo == "livro"
    assert referencia.texto_puro == (
        "DINIZ, Maria Helena. Curso de Direito Civil Brasileiro. 38 ed. "
        "São Paulo: Saraiva, 2022."
    )
    assert referencia.texto_markdown == (
        "DINIZ, Maria Helena. **Curso de Direito Civil Brasileiro**. 38 ed. "
        "São Paulo: Saraiva, 2022."
    )


def test_format_book_sem_ano_nao_deixa_virgula_pendente() -> None:
    """Sem ano, a imprenta termina de forma limpa."""
    referencia = FORMATADOR.format_book(
        author="Autor Teste", title="Obra", city="Rio de Janeiro", publisher="Editora X"
    )

    assert referencia.texto_puro == "TESTE, Autor. Obra. Rio de Janeiro: Editora X."


def test_format_journal_article_destaca_periodico() -> None:
    """Artigo: o negrito vai para o título do periódico."""
    referencia = FORMATADOR.format_journal_article(
        author="Carlos Alberto dos Santos",
        article_title="Impactos da Inteligência Artificial no Direito",
        journal_title="Revista Brasileira de Tecnologia",
        city="Brasília",
        volume="12",
        number="2",
        pages="45-60",
        year=2024,
    )

    assert referencia.tipo == "artigo"
    assert referencia.texto_puro == (
        "SANTOS, Carlos Alberto dos. Impactos da Inteligência Artificial no Direito. "
        "Revista Brasileira de Tecnologia, Brasília, v. 12, n. 2, p. 45-60, 2024."
    )
    assert "**Revista Brasileira de Tecnologia**" in referencia.texto_markdown


def test_format_website_com_autor() -> None:
    """Site com autor: 'Disponível em' e 'Acesso em'."""
    referencia = FORMATADOR.format_website(
        author="Instituto Brasileiro de Geografia e Estatística",
        title="Censo Demográfico 2022",
        url="https://www.ibge.gov.br/censo",
        access_date=datetime(2026, 1, 10),
    )

    assert referencia.tipo == "site"
    assert referencia.texto_puro == (
        "ESTATÍSTICA, Instituto Brasileiro de Geografia e. Censo Demográfico 2022. "
        "Disponível em: <https://www.ibge.gov.br/censo>. Acesso em: 10 jan. 2026."
    )


def test_format_website_sem_autor_destaca_primeira_palavra() -> None:
    """Site sem autor: a primeira palavra do título fica em caixa alta e negrito."""
    referencia = FORMATADOR.format_website(
        title="Censo demográfico 2022",
        url="https://exemplo.org",
        access_date=datetime(2026, 3, 5),
    )

    assert referencia.segmentos[0] == Segmento("CENSO", negrito=True)
    assert referencia.texto_puro == (
        "CENSO demográfico 2022. Disponível em: <https://exemplo.org>. "
        "Acesso em: 5 mar. 2026."
    )


def test_sort_references_ignora_acentos() -> None:
    """A ordenação alfabética coloca 'Ávila' antes de 'Barbosa'."""
    referencias = [
        FORMATADOR.format_book(author="Bruno Barbosa", title="Zeta", city="B", publisher="P", year=2020),
        FORMATADOR.format_book(author="Álvaro Ávila", title="Alfa", city="A", publisher="P", year=2021),
    ]

    ordenadas = FORMATADOR.sort_references(referencias)

    assert ordenadas[0].texto_puro.startswith("ÁVILA")


def test_sort_references_aceita_texto_simples() -> None:
    """Também ordena uma lista de strings com marcadores markdown."""
    itens = ["**Zebra**. 2020.", "Ábaco. 2019."]

    assert FORMATADOR.sort_references(itens)[0].startswith("Ábaco")


def test_referencia_de_markdown() -> None:
    """Reconstrói os segmentos a partir do texto com ``**``."""
    referencia = Referencia.de_markdown("Autor. **Título**. Cidade: Editora, 2020.", "livro")

    assert len(referencia.segmentos) == 3
    assert referencia.segmentos[1] == Segmento("Título", negrito=True)
    assert referencia.texto_puro == "Autor. Título. Cidade: Editora, 2020."


def test_normalizar_para_ordenacao() -> None:
    """Remove acentos, caixa e espaços excedentes."""
    assert normalizar_para_ordenacao("  Ávila,  João  ") == "avila, joao"


def test_analisar_texto_bruto_de_site() -> None:
    """Texto com URL é interpretado como referência de site."""
    referencia = FORMATADOR.analisar_texto_bruto(
        "IBGE. Censo 2022. https://www.ibge.gov.br/censo"
    )

    assert referencia.tipo == "site"
    assert "Disponível em: <https://www.ibge.gov.br/censo>" in referencia.texto_puro


def test_analisar_texto_bruto_de_livro() -> None:
    """Texto com imprenta é interpretado como livro."""
    referencia = FORMATADOR.analisar_texto_bruto(
        "DINIZ, Maria Helena. Curso de Direito Civil. São Paulo: Saraiva, 2022."
    )

    assert referencia.tipo == "livro"
    assert referencia.texto_puro == (
        "DINIZ, Maria Helena. Curso de Direito Civil. São Paulo: Saraiva, 2022."
    )


def test_analisar_texto_bruto_de_artigo() -> None:
    """Texto com v./n./p. é interpretado como artigo de periódico."""
    referencia = FORMATADOR.analisar_texto_bruto(
        "SANTOS, Carlos. Impactos da IA no Direito. Revista Brasileira, Brasília, "
        "v. 12, n. 2, p. 45-60, 2024."
    )

    assert referencia.tipo == "artigo"
    assert "v. 12" in referencia.texto_puro
    assert "n. 2" in referencia.texto_puro
    assert "p. 45-60" in referencia.texto_puro


def test_analisar_texto_bruto_generico() -> None:
    """Texto sem padrão reconhecido é devolvido como referência genérica."""
    referencia = FORMATADOR.analisar_texto_bruto("Apenas uma anotação solta")

    assert referencia.tipo == "generico"
    assert referencia.texto_puro == "Apenas uma anotação solta"


def test_analisar_texto_bruto_vazio() -> None:
    """Texto vazio devolve referência sem segmentos."""
    referencia = FORMATADOR.analisar_texto_bruto("   ")

    assert referencia.segmentos == []


def test_detectar_tipo() -> None:
    """Classifica o texto por tipo de fonte."""
    assert FORMATADOR.detectar_tipo("X. Titulo. https://a.com") == "site"
    assert FORMATADOR.detectar_tipo("X. Art. Rev, Cidade, v. 1, n. 2, p. 3-4, 2020.") == "artigo"
    assert FORMATADOR.detectar_tipo("X. Livro. Cidade: Editora, 2020.") == "livro"
    assert FORMATADOR.detectar_tipo("anotação solta") == "generico"


def test_localizar_destaque_livro() -> None:
    """O destaque do livro é exatamente o título, sem o ponto final."""
    texto = "DINIZ, Maria Helena. Curso de Direito Civil. 38 ed. São Paulo: Saraiva, 2022."
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Curso de Direito Civil"


def test_localizar_destaque_livro_com_iniciais_no_autor() -> None:
    """Autor com iniciais não confunde a localização do título."""
    texto = "SILVA, J. A. Manual de Processo Civil. São Paulo: RT, 2019."
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Manual de Processo Civil"


def test_localizar_destaque_artigo() -> None:
    """O destaque do artigo é exatamente o título do periódico."""
    texto = (
        "SANTOS, Carlos Alberto dos. Impactos da IA no Direito. "
        "Revista Brasileira de Tecnologia, Brasília, v. 12, n. 2, p. 45-60, 2024."
    )
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Revista Brasileira de Tecnologia"


def test_localizar_destaque_site_sem_autor() -> None:
    """Site sem autor destaca apenas a primeira palavra do título."""
    texto = "Censo demográfico 2022. Disponível em: <https://exemplo.org>. Acesso em: 5 mar. 2026."
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Censo"


def test_localizar_destaque_site_com_autor_nao_destaca() -> None:
    """Site com autor não recebe negrito (regra da NBR 6023 adotada)."""
    texto = (
        "IBGE. Censo 2022. Disponível em: <https://www.ibge.gov.br>. "
        "Acesso em: 10 jan. 2026."
    )

    assert FORMATADOR.localizar_destaque(texto) is None


def test_localizar_destaque_generico() -> None:
    """Texto sem padrão reconhecido não recebe destaque."""
    assert FORMATADOR.localizar_destaque("Anotação qualquer sem padrão") is None


def test_localizar_destaque_artigo_com_multiplos_autores() -> None:
    """A vírgula de 'SOBRENOME, Nome' não é confundida com a da cidade."""
    texto = (
        "ALVES, Ana; COSTA, Bruno. Redes Neurais Aplicadas. "
        "Revista de Computação, v. 3, n. 1, p. 10-20, 2023."
    )
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Revista de Computação"


def test_localizar_destaque_livro_com_et_al() -> None:
    """O 'et al.' (que termina em ponto) não desloca o título do livro."""
    texto = "SILVA, João da et al. Direito Constitucional. São Paulo: Saraiva, 2021."
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "Direito Constitucional"


def test_localizar_destaque_site_com_nome_do_site() -> None:
    """Com autor e nome do site, o destaque vai para o nome do site."""
    texto = (
        "IBGE. Censo 2022. IBGE. Disponível em: <https://www.ibge.gov.br>. "
        "Acesso em: 10 jan. 2026."
    )
    intervalo = FORMATADOR.localizar_destaque(texto)

    assert intervalo is not None
    assert texto[intervalo[0] : intervalo[1]] == "IBGE"


def test_format_authors_ate_tres() -> None:
    """Até três autores, todos são indicados separados por ponto e vírgula."""
    assert FORMATADOR.format_authors(["João da Silva"]) == "SILVA, João da. "
    assert (
        FORMATADOR.format_authors(["João da Silva", "Maria Souza"])
        == "SILVA, João da; SOUZA, Maria. "
    )
    assert FORMATADOR.format_authors(
        ["João da Silva", "Maria Souza", "Pedro Lima"]
    ) == "SILVA, João da; SOUZA, Maria; LIMA, Pedro. "


def test_format_authors_mais_de_tres_usa_et_al() -> None:
    """Acima de três autores, indica-se apenas o primeiro seguido de et al."""
    autores = ["João da Silva", "Maria Souza", "Pedro Lima", "Ana Alves"]

    assert FORMATADOR.format_authors(autores) == "SILVA, João da et al. "


def test_format_authors_vazio() -> None:
    """Sem autores, o trecho é vazio."""
    assert FORMATADOR.format_authors([]) == ""
    assert FORMATADOR.format_authors(None) == ""


def test_format_book_com_multiplos_autores() -> None:
    """O livro reúne os autores com ponto e vírgula antes do título."""
    referencia = FORMATADOR.format_book(
        authors=["João da Silva", "Maria Souza", "Pedro Lima", "Ana Alves"],
        title="Direito Constitucional",
        city="São Paulo",
        publisher="Saraiva",
        year=2021,
    )

    assert referencia.texto_puro.startswith("SILVA, João da et al. ")
    assert "**Direito Constitucional**" in referencia.texto_markdown


def test_format_journal_article_com_multiplos_autores() -> None:
    """O artigo aceita a lista de autores."""
    referencia = FORMATADOR.format_journal_article(
        authors=["Ana Alves", "Bruno Costa"],
        article_title="Redes Neurais",
        journal_title="Revista de Computação",
        volume="3",
        number="1",
        pages="10-20",
        year=2023,
    )

    assert referencia.texto_puro.startswith("ALVES, Ana; COSTA, Bruno. ")
    assert "**Revista de Computação**" in referencia.texto_markdown


def test_format_website_com_nome_do_site() -> None:
    """O nome do site recebe o negrito quando informado."""
    referencia = FORMATADOR.format_website(
        authors=["Instituto Brasileiro de Geografia e Estatística"],
        title="Censo 2022",
        site_name="IBGE",
        url="https://www.ibge.gov.br",
        access_date=datetime(2026, 5, 20),
    )

    assert "**IBGE**" in referencia.texto_markdown
    assert referencia.texto_puro.endswith("Acesso em: 20 maio 2026.")
    assert "Censo 2022" in referencia.texto_puro


def test_format_website_com_nome_do_site_tem_acento_no_mes_de_maio() -> None:
    """A NBR 6023 não abrevia o mês de maio."""
    referencia = FORMATADOR.format_website(
        title="Notícia",
        url="https://exemplo.org",
        access_date=datetime(2026, 5, 1),
    )

    assert "1 maio 2026" in referencia.texto_puro
    assert "mai." not in referencia.texto_puro


def test_meses_abnt_nao_abrevia_maio() -> None:
    """A tabela de meses mantém 'maio' por extenso."""
    assert MESES_ABNT[5] == "maio"
    assert MESES_ABNT[1] == "jan."
    assert MESES_ABNT[12] == "dez."


def test_ajustar_intervalo() -> None:
    """O intervalo é recolhido removendo espaços e pontuação das bordas."""
    assert ajustar_intervalo("  Título.  ", 0, 11) == (2, 8)
    assert ajustar_intervalo("   ", 0, 3) is None
