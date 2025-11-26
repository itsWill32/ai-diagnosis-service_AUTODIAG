
from uuid import UUID, uuid4
from typing import Protocol, Optional, Dict, Any
from datetime import datetime

from app.application.dtos.request import AnalyzeSentimentDto
from app.application.dtos.response import SentimentAnalysisDto, SentimentResultDto, SentimentScoresDto


class SentimentAnalyzerService(Protocol):
    
    async def analyze(self, text: str) -> dict:

        ...


class AnalyzeSentimentUseCase:

    
    def __init__(self, sentiment_analyzer: SentimentAnalyzerService):
        self.sentiment_analyzer = sentiment_analyzer
    
    async def execute(self, dto: AnalyzeSentimentDto) -> SentimentAnalysisDto:

        sentiment_result = await self.sentiment_analyzer.analyze(text=dto.text)
        
        sentiment_scores = SentimentScoresDto(
            positive=sentiment_result['scores']['positive'],
            neutral=sentiment_result['scores']['neutral'],
            negative=sentiment_result['scores']['negative']
        )
        
        sentiment = SentimentResultDto(
            label=sentiment_result['label'],
            score=sentiment_result['score'],
            scores=sentiment_scores
        )
        
        return SentimentAnalysisDto(
            id=uuid4(),
            text=dto.text,
            sentiment=sentiment,
            context=dto.context,
            analyzed_at=datetime.utcnow()
        )