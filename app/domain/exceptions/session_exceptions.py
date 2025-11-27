
class SessionDomainException(Exception):
    pass


class SessionNotFoundException(SessionDomainException):
    def __init__(self, session_id: str):
        super().__init__(f"La sesión {session_id} no fue encontrada")
        self.session_id = session_id


class SessionNotOwnedByUserException(SessionDomainException):
    def __init__(self, session_id: str, user_id: str):
        super().__init__(f"La sesión {session_id} no pertenece al usuario {user_id}")
        self.session_id = session_id
        self.user_id = user_id


class SessionNotActiveException(SessionDomainException):
    def __init__(self, session_id: str, current_status: str):
        super().__init__(
            f"No se pueden enviar mensajes a la sesión {session_id}. "
            f"Estado actual: {current_status}"
        )
        self.session_id = session_id
        self.current_status = current_status


class InvalidSessionStatusException(SessionDomainException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Transición de estado inválida: {current_status} → {target_status}"
        )
        self.current_status = current_status
        self.target_status = target_status


class InsufficientMessagesException(SessionDomainException):
    def __init__(self, session_id: str, required: int, actual: int):
        super().__init__(
            f"La sesión {session_id} necesita al menos {required} mensajes "
            f"para clasificación. Actual: {actual}"
        )
        self.session_id = session_id
        self.required = required
        self.actual = actual