
from typing import Protocol, Optional, List
from uuid import UUID


class AnalyticsRepository(Protocol):
    
    async def get_workshops_performance(
        self,
        workshop_id: Optional[UUID],
        sort_by: str,
        limit: int
    ) -> List[dict]:
        ...


class GetWorkshopsPerformanceUseCase:
    
    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
    
    async def execute(
        self,
        workshop_id: Optional[UUID] = None,
        sort_by: str = 'rating',
        limit: int = 20
    ) -> List[dict]:

        return await self.analytics_repository.get_workshops_performance(
            workshop_id=workshop_id,
            sort_by=sort_by,
            limit=limit
        )