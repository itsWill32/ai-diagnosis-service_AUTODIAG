
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SessionId:

    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError(f"SessionId debe ser un UUID válido, recibido: {type(self.value)}")
    
    @classmethod
    def from_string(cls, session_id: str) -> 'SessionId':

        try:
            uuid_value = UUID(session_id)
            return cls(value=uuid_value)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"SessionId inválido: {session_id}") from e
    
    def to_string(self) -> str:

        return str(self.value)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"SessionId(value='{self.value}')"