
from typing import Protocol, List
from uuid import uuid4
from datetime import datetime

from app.application.dtos.response import SentimentResultDto, SentimentScoresDto


class SentimentAnalyzerService(Protocol):
    """Servicio ML para análisis de sentimientos."""
    
    async def analyze_batch(self, texts: List[str]) -> List[dict]:

        ...


class BatchAnalyzeSentimentUseCase:

    
    MAX_BATCH_SIZE = 100
    
    def __init__(self, sentiment_analyzer: SentimentAnalyzerService):
        self.sentiment_analyzer = sentiment_analyzer
    
    async def execute(
        self,
        texts: List[dict]  
    ) -> List[dict]:

        if len(texts) > self.MAX_BATCH_SIZE:
            raise BatchSizeTooLargeException(
                f"El tamaño {len(texts)} excede el máximo de {self.MAX_BATCH_SIZE}"
            )
        
        text_list = [item['text'] for item in texts]
        
        results = await self.sentiment_analyzer.analyze_batch(texts=text_list)
        
        output = []
        for i, original_item in enumerate(texts):
            sentiment_result = results[i]
            
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
            
            output.append({
                'id': original_item['id'],
                'sentiment': sentiment.model_dump()
            })
        
        return output


class BatchSizeTooLargeException(Exception):
    """El batch supera el tamaño máximo."""
    pass