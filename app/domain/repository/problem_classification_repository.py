

from typing import Protocol, Optional
from uuid import UUID
from datetime import datetime

from ..entities import ProblemClassification


class ProblemClassificationRepository(Protocol):

    
    async def save(
        self,
        classification: ProblemClassification,
    ) -> ProblemClassification:

        ...
    
    async def find_by_id(
        self,
        classification_id: UUID,
    ) -> Optional[ProblemClassification]:

        ...
    
    async def find_by_session_id(
        self,
        session_id: UUID,
    ) -> Optional[ProblemClassification]:

        ...
    
    async def delete(self, classification_id: UUID) -> None:

        ...
    
    
    async def count_by_category(
        self,
        category: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> int:

        ...
    
    async def get_category_distribution(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> dict[str, int]:

        ...
    
    async def get_top_categories(
        self,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> list[tuple[str, int]]:

        ...
    
    async def get_average_confidence_by_category(
        self,
        category: str,
    ) -> float:

        ...