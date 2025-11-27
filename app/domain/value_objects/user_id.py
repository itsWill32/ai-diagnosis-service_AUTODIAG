

from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass(frozen=True)
class UserId:

    
    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError(f"UserId debe ser un UUID válido, recibido: {type(self.value)}")
    
    @classmethod
    def from_string(cls, user_id_str: str) -> 'UserId':

        try:
            uuid_obj = UUID(user_id_str)
            return cls(value=uuid_obj)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"String inválido para UserId: {user_id_str}") from e
    
    def to_string(self) -> str:
        return str(self.value)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"UserId('{self.to_string()}')"