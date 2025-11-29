

from enum import Enum


class SessionStatus(str, Enum):
    
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    
    def is_active(self) -> bool:
        return self == SessionStatus.ACTIVE
    
    def is_completed(self) -> bool:
        return self == SessionStatus.COMPLETED
    
    def is_abandoned(self) -> bool:
        return self == SessionStatus.ABANDONED
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"SessionStatus.{self.name}"