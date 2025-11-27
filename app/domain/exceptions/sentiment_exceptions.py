
class SentimentDomainException(Exception):
    """Excepción base para errores de dominio de análisis de sentimientos"""
    pass


class TextTooLongException(SentimentDomainException):
    def __init__(self, length: int, max_length: int):
        super().__init__(
            f"Texto demasiado largo: {length} caracteres "
            f"(máximo: {max_length})"
        )
        self.length = length
        self.max_length = max_length


class EmptyTextException(SentimentDomainException):
    def __init__(self):
        super().__init__("El texto para análisis de sentimiento no puede estar vacío")


class BatchSizeTooLargeException(SentimentDomainException):
    def __init__(self, batch_size: int, max_batch_size: int):
        super().__init__(
            f"Batch de {batch_size} textos excede el máximo permitido "
            f"de {max_batch_size}"
        )
        self.batch_size = batch_size
        self.max_batch_size = max_batch_size