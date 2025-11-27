

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
        
        existing = await self.db.sentimentanalysis.find_unique(
            where={"id": str(sentiment_analysis.analysis_id)}
        )
        
        if existing:
            await self.db.sentimentanalysis.update(
                where={"id": str(sentiment_analysis.analysis_id)},
                data={
                    "text": sentiment_dict["text"],
                    "sentimentLabel": label_value,
                    "confidenceScore": float(sentiment_dict["confidence_score"]),
                    "positiveScore": float(sentiment_dict["positive_score"]),
                    "neutralScore": float(sentiment_dict["neutral_score"]),
                    "negativeScore": float(sentiment_dict["negative_score"]),
                    "context": sentiment_dict.get("context"),
                }
            )
        else:
            await self.db.sentimentanalysis.create(
                data={
                    "id": str(sentiment_analysis.analysis_id),
                    "text": sentiment_dict["text"],
                    "sentimentLabel": label_value,
                    "confidenceScore": float(sentiment_dict["confidence_score"]),
                    "positiveScore": float(sentiment_dict["positive_score"]),
                    "neutralScore": float(sentiment_dict["neutral_score"]),
                    "negativeScore": float(sentiment_dict["negative_score"]),
                    "context": sentiment_dict.get("context"),
                }
            )
    
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
    
    
    def _to_domain(self, prisma_sentiment: PrismaSentimentAnalysis) -> SentimentAnalysis:

        sentiment_dict = {
            "analysis_id": str(prisma_sentiment.id),
            "text": prisma_sentiment.text,
            "sentiment_label": prisma_sentiment.sentimentLabel,
            "confidence_score": prisma_sentiment.confidenceScore,
            "positive_score": prisma_sentiment.positiveScore,
            "neutral_score": prisma_sentiment.neutralScore,
            "negative_score": prisma_sentiment.negativeScore,
            "context": prisma_sentiment.context,
            "analyzed_at": prisma_sentiment.analyzedAt.isoformat(),
        }
        
        return SentimentAnalysis.from_primitives(sentiment_dict)