

class ClassificationDomainException(Exception):
    """Excepción base para errores de dominio de clasificación"""
    pass


class ClassificationNotFoundException(ClassificationDomainException):
    def __init__(self, session_id: str):
        super().__init__(
            f"No se encontró clasificación para la sesión {session_id}"
        )
        self.session_id = session_id


class InsufficientDataForClassificationException(ClassificationDomainException):
    def __init__(self, session_id: str, reason: str):
        super().__init__(
            f"Datos insuficientes para clasificar sesión {session_id}: {reason}"
        )
        self.session_id = session_id
        self.reason = reason


class LowConfidenceClassificationException(ClassificationDomainException):
    def __init__(self, session_id: str, confidence: float, threshold: float):
        super().__init__(
            f"Confianza de clasificación muy baja para sesión {session_id}: "
            f"{confidence:.2%} (mínimo: {threshold:.2%})"
        )
        self.session_id = session_id
        self.confidence = confidence
        self.threshold = threshold