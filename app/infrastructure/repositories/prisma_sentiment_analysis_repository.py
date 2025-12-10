

from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

from prisma import Prisma
from prisma.models import SentimentAnalysis as PrismaSentimentAnalysis

from app.domain.entities import SentimentAnalysis
from app.domain.repository import SentimentAnalysisRepository
from app.domain.value_objects import SentimentLabel


class PrismaSentimentAnalysisRepository(SentimentAnalysisRepository):

    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def save(self, sentiment_analysis: SentimentAnalysis) -> None:

        sentiment_dict = sentiment_analysis.to_dict()

        label_value = sentiment_dict["sentiment_label"].value if hasattr(sentiment_dict["sentiment_label"], "value") else str(sentiment_dict["sentiment_label"])

        # Preparar scores JSON
        scores_json = {
            "positive": float(sentiment_dict["positive_score"]),
            "neutral": float(sentiment_dict["neutral_score"]),
            "negative": float(sentiment_dict["negative_score"])
        }

        existing = await self.db.sentimentanalysis.find_unique(
            where={"id": str(sentiment_analysis.id)}
        )

        data_dict = {
            "text": sentiment_dict["text"],
            "label": label_value,
            "score": float(sentiment_dict["confidence_score"]),
            "scores": scores_json,
            "context": sentiment_dict.get("context"),
            "workshopId": str(sentiment_analysis.workshop_id) if sentiment_analysis.workshop_id else None,
        }

        if existing:
            await self.db.sentimentanalysis.update(
                where={"id": str(sentiment_analysis.id)},
                data=data_dict
            )
        else:
            data_dict["id"] = str(sentiment_analysis.id)
            await self.db.sentimentanalysis.create(data=data_dict)
    
    async def find_by_id(self, analysis_id: UUID) -> Optional[SentimentAnalysis]:

        prisma_sentiment = await self.db.sentimentanalysis.find_unique(
            where={"id": str(analysis_id)}
        )
        
        if not prisma_sentiment:
            return None
        
        return self._to_domain(prisma_sentiment)
    
    async def find_by_context(
        self,
        context_key: str,
        context_value: str
    ) -> Optional[SentimentAnalysis]:


        all_sentiments = await self.db.sentimentanalysis.find_many(
            where={
                "context": {
                    "path": [context_key],
                    "equals": context_value
                }
            }
        )
        
        if not all_sentiments:
            return None
        
        return self._to_domain(all_sentiments[0])
    
    async def delete(self, analysis_id: UUID) -> None:

        await self.db.sentimentanalysis.delete(
            where={"id": str(analysis_id)}
        )
    
    
    async def count_by_sentiment(
        self,
        sentiment_label: SentimentLabel,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> int:

        where_clause = {"sentimentLabel": sentiment_label.value}
        
        if from_date:
            where_clause["analyzedAt"] = {"gte": from_date}
        if to_date:
            where_clause["analyzedAt"] = {**where_clause.get("analyzedAt", {}), "lte": to_date}
        
        return await self.db.sentimentanalysis.count(where=where_clause)
    
    async def get_sentiment_distribution(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, int]:

        where_clause = {}
        
        if from_date:
            where_clause["analyzedAt"] = {"gte": from_date}
        if to_date:
            where_clause["analyzedAt"] = {**where_clause.get("analyzedAt", {}), "lte": to_date}
        
        sentiments = await self.db.sentimentanalysis.find_many(
            where=where_clause,
            select={"sentimentLabel": True}
        )
        
        distribution = {}
        for s in sentiments:
            label = s.sentimentLabel
            distribution[label] = distribution.get(label, 0) + 1
        
        return distribution
    
    async def get_average_sentiment_score(
        self,
        context_key: Optional[str] = None,
        context_value: Optional[str] = None
    ) -> float:

        where_clause = {}
        
        if context_key and context_value:
            where_clause["context"] = {
                "path": [context_key],
                "equals": context_value
            }
        
        sentiments = await self.db.sentimentanalysis.find_many(
            where=where_clause,
            select={"sentimentLabel": True}
        )
        
        if not sentiments:
            return 0.0
        
        score_map = {"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}
        scores = [score_map.get(s.sentimentLabel, 0.0) for s in sentiments]
        
        return sum(scores) / len(scores)
    
    async def count_total(self) -> int:

        return await self.db.sentimentanalysis.count()

    async def get_sentiment_score_by_workshop(self, workshop_id: str) -> float:
        """
        Obtiene el score de sentimiento promedio para un taller específico

        Args:
            workshop_id: ID del taller

        Returns:
            float: Score promedio (-1.0 a 1.0)
        """
        sentiments = await self.db.sentimentanalysis.find_many(
            where={"workshopId": workshop_id}
        )

        if not sentiments:
            return 0.0

        # Mapear labels a scores numéricos
        score_map = {"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}
        scores = [score_map.get(s.label, 0.0) for s in sentiments]

        return sum(scores) / len(scores)


    async def create(self, sentiment_analysis: SentimentAnalysis) -> SentimentAnalysis:
        """
        Crea un nuevo análisis de sentimiento en la base de datos

        Args:
            sentiment_analysis: Entidad de dominio

        Returns:
            SentimentAnalysis: Entidad creada
        """
        await self.save(sentiment_analysis)
        return sentiment_analysis


    def _to_domain(self, prisma_sentiment: PrismaSentimentAnalysis) -> SentimentAnalysis:

        # Extraer scores del JSON
        scores = prisma_sentiment.scores if hasattr(prisma_sentiment, 'scores') else {}
        if isinstance(scores, dict):
            positive_score = scores.get('positive', 0.0)
            neutral_score = scores.get('neutral', 0.0)
            negative_score = scores.get('negative', 0.0)
        else:
            positive_score = 0.0
            neutral_score = 0.0
            negative_score = 0.0

        return SentimentAnalysis.from_primitives(
            analysis_id=str(prisma_sentiment.id),
            text=prisma_sentiment.text,
            sentiment_label=prisma_sentiment.label,
            confidence_score=prisma_sentiment.score,
            positive_score=positive_score,
            neutral_score=neutral_score,
            negative_score=negative_score,
            context=prisma_sentiment.context,
            analyzed_at=prisma_sentiment.analyzedAt,
            workshop_id=prisma_sentiment.workshopId if hasattr(prisma_sentiment, 'workshopId') else None
        )