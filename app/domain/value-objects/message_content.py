
from dataclasses import dataclass


@dataclass(frozen=True)
class MessageContent:

    value: str
    
    MAX_LENGTH = 2000  
    MIN_LENGTH = 1
    
    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(f"MessageContent debe ser un string, recibido: {type(self.value)}")
        
        content = self.value.strip()
        if len(content) < self.MIN_LENGTH:
            raise ValueError("El contenido del mensaje no puede estar vacío")
        
        if len(content) > self.MAX_LENGTH:
            raise ValueError(
                f"El contenido del mensaje no puede exceder {self.MAX_LENGTH} caracteres. "
                f"Recibido: {len(content)} caracteres"
            )
    
    @classmethod
    def create(cls, content: str) -> 'MessageContent':

        cleaned_content = content.strip()
        return cls(value=cleaned_content)
    
    def to_string(self) -> str:

        return self.value
    
    def is_empty(self) -> bool:

        return len(self.value.strip()) == 0
    
    def word_count(self) -> int:

        return len(self.value.split())
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        preview = self.value[:50] + "..." if len(self.value) > 50 else self.value
        return f"MessageContent(value='{preview}')"