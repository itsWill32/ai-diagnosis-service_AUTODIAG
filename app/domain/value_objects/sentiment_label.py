

from enum import Enum


class SentimentLabel(str, Enum):
    
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    
    def is_positive(self) -> bool:
        return self == SentimentLabel.POSITIVE
    
    def is_neutral(self) -> bool:
        return self == SentimentLabel.NEUTRAL
    
    def is_negative(self) -> bool:
        return self == SentimentLabel.NEGATIVE
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"SentimentLabel.{self.name}"