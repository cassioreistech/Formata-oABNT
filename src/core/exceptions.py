"""Exceções customizadas do Formata-oABNT."""


class FormataABNTError(Exception):
    """Exceção base do sistema."""

    def __init__(self, message: str, norma: str | None = None) -> None:
        self.norma = norma
        super().__init__(message)


class ValidationError(FormataABNTError):
    """Erro de validação de conformidade ABNT."""

    def __init__(self, message: str, field: str, norma: str | None = None) -> None:
        self.field = field
        super().__init__(message, norma)


class DocumentTypeError(FormataABNTError):
    """Tipo de documento não suportado."""

    def __init__(self, tipo: str) -> None:
        super().__init__(f"Tipo de documento não suportado: {tipo}")


class GeneratorError(FormataABNTError):
    """Erro na geração do documento."""


class ParserError(FormataABNTError):
    """Erro no parsing de entrada."""