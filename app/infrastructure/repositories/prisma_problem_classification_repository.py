

from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

from prisma import Prisma
from prisma.models import ProblemClassification as PrismaProblemClassification

from app.domain.entities.problem_classification import ProblemClassification
from app.domain.value_objects.problem_category import ProblemCategory


class PrismaProblemClassificationRepository:
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def save(self, classification: ProblemClassification) -> ProblemClassification:
        class_dict = classification.to_dict()
        
        existing = await self.db.problemclassification.find_unique(
            where={"id": str(classification.id)}
        )
        
        if existing:
            await self.db.problemclassification.update(
                where={"id": str(classification.id)},
                data={
                    "category": class_dict["category"],
                    "subcategory": class_dict.get("subcategory"),
                    "confidenceScore": class_dict["confidence_score"],
                    "symptoms": class_dict.get("symptoms", []),
                }
            )
        else:
            await self.db.problemclassification.create(
                data={
                    "id": str(classification.id),
                    "sessionId": str(classification.session_id),
                    "category": class_dict["category"],
                    "subcategory": class_dict.get("subcategory"),
                    "confidenceScore": class_dict["confidence_score"],
                    "symptoms": class_dict.get("symptoms", []),
                }
            )
        
        return classification
    
    async def find_by_id(self, classification_id: UUID) -> Optional[ProblemClassification]:
        prisma_class = await self.db.problemclassification.find_unique(
            where={"id": str(classification_id)}
        )
        
        if not prisma_class:
            return None
        
        return self._to_domain(prisma_class)
    
    async def find_by_session_id(self, session_id: UUID) -> Optional[ProblemClassification]:
        prisma_class = await self.db.problemclassification.find_unique(
            where={"sessionId": str(session_id)}
        )
        
        if not prisma_class:
            return None
        
        return self._to_domain(prisma_class)
    
    async def delete(self, classification_id: UUID) -> None:
        await self.db.problemclassification.delete(
            where={"id": str(classification_id)}
        )
    
    
    async def count_by_category(
        self,
        category: ProblemCategory,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> int:
        where_clause = {"category": category.value}
        
        if from_date:
            where_clause["createdAt"] = {"gte": from_date}
        if to_date:
            where_clause.setdefault("createdAt", {})["lte"] = to_date
        
        return await self.db.problemclassification.count(where=where_clause)
    
    async def get_category_distribution(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        where_clause = {}
        
        if from_date:
            where_clause["createdAt"] = {"gte": from_date}
        if to_date:
            where_clause.setdefault("createdAt", {})["lte"] = to_date
        
        classifications = await self.db.problemclassification.find_many(
            where=where_clause,
            select={"category": True}
        )
        
        distribution = {}
        for c in classifications:
            category = c.category
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    async def get_top_categories(
        self,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[tuple[str, int]]:
        distribution = await self.get_category_distribution(from_date, to_date)
        
        sorted_categories = sorted(
            distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_categories[:limit]
    
    async def get_average_confidence_by_category(
        self,
        category: ProblemCategory
    ) -> float:
        classifications = await self.db.problemclassification.find_many(
            where={"category": category.value},
            select={"confidenceScore": True}
        )
        
        if not classifications:
            return 0.0
        
        total = sum(c.confidenceScore for c in classifications)
        return total / len(classifications)
    
    def _to_domain(
        self,
        prisma_class: PrismaProblemClassification
    ) -> ProblemClassification:
        return ProblemClassification.from_primitives(
            classification_id=prisma_class.id,
            session_id=prisma_class.sessionId,
            category=prisma_class.category,
            subcategory=prisma_class.subcategory,
            confidence_score=prisma_class.confidenceScore,
            symptoms=prisma_class.symptoms if prisma_class.symptoms else [],
            created_at=prisma_class.createdAt
        )