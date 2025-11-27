
from typing import Protocol, Optional
from uuid import UUID
from datetime import datetime

from ..entities import SentimentAnalysis


class SentimentAnalysisRepository(Protocol):

    
    async def save(
        self,
        sentiment_analysis: SentimentAnalysis,
    ) -> SentimentAnalysis:

        ...
    
    async def find_by_id(
        self,
        analysis_id: UUID,
    ) -> Optional[SentimentAnalysis]:

        ...
    
    async def find_by_context(
        self,
        context_key: str,
        context_value: str,
    ) -> list[SentimentAnalysis]:

        ...
    
    async def delete(self, analysis_id: UUID) -> None:

        ...
    
    
    async def count_by_sentiment(
        self,
        sentiment_label: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> int:

        ...
    
    async def get_sentiment_distribution(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> dict[str, int]:

        ...
    
    async def get_average_sentiment_score(
        self,
        context_key: Optional[str] = None,
        context_value: Optional[str] = None,
    ) -> float:

        ...
    
    async def count_total(self) -> int:

        ...