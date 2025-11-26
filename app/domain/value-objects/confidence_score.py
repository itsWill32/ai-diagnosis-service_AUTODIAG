
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceScore:

    value: float
    
    MIN_SCORE = 0.0
    MAX_SCORE = 1.0
    
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValueError(
                f"ConfidenceScore debe ser numérico, recibido: {type(self.value)}"
            )
        
        object.__setattr__(self, 'value', float(self.value))
        
        if not (self.MIN_SCORE <= self.value <= self.MAX_SCORE):
            raise ValueError(
                f"ConfidenceScore debe estar entre {self.MIN_SCORE} y {self.MAX_SCORE}, "
                f"recibido: {self.value}"
            )
    
    @classmethod
    def create(cls, score: float) -> 'ConfidenceScore':

        return cls(value=score)
    
    @classmethod
    def from_percentage(cls, percentage: float) -> 'ConfidenceScore':

        if not (0 <= percentage <= 100):
            raise ValueError(
                f"Porcentaje debe estar entre 0 y 100, recibido: {percentage}"
            )
        return cls(value=percentage / 100.0)
    
    def to_float(self) -> float:

        return self.value
    
    def to_percentage(self) -> float:

        return self.value * 100.0
    
    def is_high_confidence(self) -> bool:

        return self.value >= self.HIGH_CONFIDENCE_THRESHOLD
    
    def is_medium_confidence(self) -> bool:

        return (
            self.MEDIUM_CONFIDENCE_THRESHOLD <= self.value < self.HIGH_CONFIDENCE_THRESHOLD
        )
    
    def is_low_confidence(self) -> bool:

        return self.value < self.MEDIUM_CONFIDENCE_THRESHOLD
    
    def get_confidence_level(self) -> str:

        if self.is_high_confidence():
            return "HIGH"
        elif self.is_medium_confidence():
            return "MEDIUM"
        else:
            return "LOW"
    
    def is_reliable(self) -> bool:

        return self.value >= self.MEDIUM_CONFIDENCE_THRESHOLD
    
    def __float__(self) -> float:
        return self.value
    
    def __str__(self) -> str:
        return f"{self.to_percentage():.2f}%"
    
    def __repr__(self) -> str:
        return f"ConfidenceScore(value={self.value:.4f}, level={self.get_confidence_level()})"
    
    def __lt__(self, other: 'ConfidenceScore') -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self.value < other.value
    
    def __le__(self, other: 'ConfidenceScore') -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self.value <= other.value
    
    def __gt__(self, other: 'ConfidenceScore') -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self.value > other.value
    
    def __ge__(self, other: 'ConfidenceScore') -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self.value >= other.value