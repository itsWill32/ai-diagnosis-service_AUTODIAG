

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MessageId:
    
    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError(f"MessageId debe ser un UUID válido, recibido: {type(self.value)}")
    
    @classmethod
    def generate(cls) -> 'MessageId':
        return cls(value=uuid4())
    
    @classmethod
    def from_string(cls, message_id: str) -> 'MessageId':
        try:
            uuid_value = UUID(message_id)
            return cls(value=uuid_value)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"MessageId inválido: {message_id}") from e
    
    def to_string(self) -> str:
        return str(self.value)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"MessageId(value='{self.value}')"