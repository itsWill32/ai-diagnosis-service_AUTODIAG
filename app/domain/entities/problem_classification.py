

from datetime import datetime
from typing import Optional
from uuid import UUID

from ..value_objects import (
    ProblemCategory,
    ConfidenceScore,
)
from ..exceptions import (
    LowConfidenceClassificationException,
)


class ProblemClassification:

    
    MIN_CONFIDENCE_THRESHOLD = 0.5  
    
    def __init__(
        self,
        classification_id: UUID,
        session_id: UUID,
        category: ProblemCategory,
        subcategory: Optional[str],
        confidence_score: ConfidenceScore,
        symptoms: list[str],
        created_at: Optional[datetime] = None,
    ):
        self._classification_id = classification_id
        self._session_id = session_id
        self._category = category
        self._subcategory = subcategory
        self._confidence_score = confidence_score
        self._symptoms = symptoms
        self._created_at = created_at or datetime.utcnow()
        
        if confidence_score.value < self.MIN_CONFIDENCE_THRESHOLD:
            raise LowConfidenceClassificationException(
                session_id=str(session_id),
                confidence=confidence_score.value,
                threshold=self.MIN_CONFIDENCE_THRESHOLD,
            )
    
    @staticmethod
    def create(
        session_id: UUID,
        category: str,
        subcategory: Optional[str],
        confidence: float,
        symptoms: list[str],
    ) -> "ProblemClassification":
        """Factory method para crear una nueva clasificación"""
        
        from uuid import uuid4
        
        return ProblemClassification(
            classification_id=uuid4(),
            session_id=session_id,
            category=ProblemCategory(category),
            subcategory=subcategory,
            confidence_score=ConfidenceScore(confidence),
            symptoms=symptoms,
        )
    
    
    @property
    def id(self) -> UUID:
        return self._classification_id
    
    @property
    def session_id(self) -> UUID:
        return self._session_id
    
    @property
    def category(self) -> ProblemCategory:
        return self._category
    
    @property
    def subcategory(self) -> Optional[str]:
        return self._subcategory
    
    @property
    def confidence_score(self) -> ConfidenceScore:
        return self._confidence_score
    
    @property
    def symptoms(self) -> list[str]:
        return self._symptoms.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    def is_high_confidence(self) -> bool:
        return self._confidence_score.value >= 0.8
    
    def is_engine_related(self) -> bool:
        return self._category.value == "ENGINE"
    
    def is_critical_category(self) -> bool:
        critical_categories = ["ENGINE", "BRAKES", "TRANSMISSION"]
        return self._category.value in critical_categories
    
    def to_dict(self) -> dict:
        return {
            "id": str(self._classification_id),
            "session_id": str(self._session_id),
            "category": self._category.value,
            "subcategory": self._subcategory,
            "confidence_score": self._confidence_score.value,
            "symptoms": self._symptoms,
            "created_at": self._created_at.isoformat(),
        }
    
    @staticmethod
    def from_primitives(
        classification_id: str,
        session_id: str,
        category: str,
        subcategory: Optional[str],
        confidence_score: float,
        symptoms: list[str],
        created_at: datetime,
    ) -> "ProblemClassification":
        """Reconstruye la entidad desde primitivos"""
        
        return ProblemClassification(
            classification_id=UUID(classification_id),
            session_id=UUID(session_id),
            category=ProblemCategory(category),
            subcategory=subcategory,
            confidence_score=ConfidenceScore(confidence_score),
            symptoms=symptoms,
            created_at=created_at,
        )