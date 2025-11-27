

class MessageDomainException(Exception):
    """Excepción base para errores de dominio de mensajes"""
    pass


class InvalidMessageContentException(MessageDomainException):
    def __init__(self, reason: str):
        super().__init__(f"Contenido del mensaje inválido: {reason}")
        self.reason = reason


class TooManyAttachmentsException(MessageDomainException):
    def __init__(self, max_allowed: int, provided: int):
        super().__init__(
            f"Máximo {max_allowed} attachments permitidos. Recibidos: {provided}"
        )
        self.max_allowed = max_allowed
        self.provided = provided


class InvalidAttachmentTypeException(MessageDomainException):
    def __init__(self, attachment_type: str, allowed_types: list[str]):
        super().__init__(
            f"Tipo de attachment '{attachment_type}' no válido. "
            f"Tipos permitidos: {', '.join(allowed_types)}"
        )
        self.attachment_type = attachment_type
        self.allowed_types = allowed_types