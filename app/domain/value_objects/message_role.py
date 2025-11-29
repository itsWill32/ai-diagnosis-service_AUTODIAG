

from enum import Enum


class MessageRole(str, Enum):
    
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    
    @classmethod
    def user(cls) -> 'MessageRole':
        return cls.USER
    
    @classmethod
    def assistant(cls) -> 'MessageRole':
        return cls.ASSISTANT
    
    def is_user(self) -> bool:
        return self == MessageRole.USER
    
    def is_assistant(self) -> bool:
        return self == MessageRole.ASSISTANT
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"MessageRole.{self.name}"