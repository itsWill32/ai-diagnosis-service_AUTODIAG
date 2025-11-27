

from datetime import datetime
from typing import Optional
from uuid import UUID

from ..value_objects import SentimentLabel
from ..exceptions import (
    TextTooLongException,
    EmptyTextException,
)


class SentimentAnalysis:

    
    MAX_TEXT_LENGTH = 5000
    
    def __init__(
        self,
        analysis_id: UUID,
        text: str,
        sentiment_label: SentimentLabel,
        confidence_score: float,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
        context: Optional[dict] = None,
        analyzed_at: Optional[datetime] = None,
    ):
        if not text or text.strip() == "":
            raise EmptyTextException()
        
        if len(text) > self.MAX_TEXT_LENGTH:
            raise TextTooLongException(
                length=len(text),
                max_length=self.MAX_TEXT_LENGTH,
            )
        
        self._analysis_id = analysis_id
        self._text = text
        self._sentiment_label = sentiment_label
        self._confidence_score = confidence_score
        self._positive_score = positive_score
        self._neutral_score = neutral_score
        self._negative_score = negative_score
        self._context = context or {}
        self._analyzed_at = analyzed_at or datetime.utcnow()
    
    @staticmethod
    def create(
        text: str,
        sentiment_label: str,
        confidence_score: float,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
        context: Optional[dict] = None,
    ) -> "SentimentAnalysis":
        """Factory method para crear un nuevo análisis"""
        
        from uuid import uuid4
        
        return SentimentAnalysis(
            analysis_id=uuid4(),
            text=text,
            sentiment_label=SentimentLabel(sentiment_label),
            confidence_score=confidence_score,
            positive_score=positive_score,
            neutral_score=neutral_score,
            negative_score=negative_score,
            context=context,
        )
    
    
    
    @property
    def id(self) -> UUID:
        return self._analysis_id
    
    @property
    def text(self) -> str:
        return self._text
    
    @property
    def sentiment_label(self) -> SentimentLabel:
        return self._sentiment_label
    
    @property
    def confidence_score(self) -> float:
        return self._confidence_score
    
    @property
    def positive_score(self) -> float:
        return self._positive_score
    
    @property
    def neutral_score(self) -> float:
        return self._neutral_score
    
    @property
    def negative_score(self) -> float:
        return self._negative_score
    
    @property
    def context(self) -> dict:
        return self._context.copy()
    
    @property
    def analyzed_at(self) -> datetime:
        return self._analyzed_at
    
    def is_positive(self) -> bool:
        return self._sentiment_label.is_positive()
    
    def is_negative(self) -> bool:
        return self._sentiment_label.is_negative()
    
    def is_neutral(self) -> bool:
        return self._sentiment_label.is_neutral()
    
    def get_dominant_sentiment_score(self) -> float:
        return max(
            self._positive_score,
            self._neutral_score,
            self._negative_score,
        )
    
    def to_dict(self) -> dict:
        return {
            "id": str(self._analysis_id),
            "text": self._text,
            "sentiment_label": self._sentiment_label.value,
            "confidence_score": self._confidence_score,
            "positive_score": self._positive_score,
            "neutral_score": self._neutral_score,
            "negative_score": self._negative_score,
            "context": self._context,
            "analyzed_at": self._analyzed_at.isoformat(),
        }
    
    @staticmethod
    def from_primitives(
        analysis_id: str,
        text: str,
        sentiment_label: str,
        confidence_score: float,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
        context: Optional[dict],
        analyzed_at: datetime,
    ) -> "SentimentAnalysis":
        """Reconstruye la entidad desde primitivos"""
        
        return SentimentAnalysis(
            analysis_id=UUID(analysis_id),
            text=text,
            sentiment_label=SentimentLabel(sentiment_label),
            confidence_score=confidence_score,
            positive_score=positive_score,
            neutral_score=neutral_score,
            negative_score=negative_score,
            context=context,
            analyzed_at=analyzed_at,
        )