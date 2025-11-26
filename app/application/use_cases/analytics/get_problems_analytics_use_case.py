
from typing import Protocol

from app.application.dtos.response import (
    ProblemsAnalyticsDto,
    CategoryDistributionDto,
    UrgencyDistributionDto
)


class AnalyticsRepository(Protocol):
    
    async def get_problems_analytics(self, period: str) -> dict:

        ...


class GetProblemsAnalyticsUseCase:
    
    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
    
    async def execute(self, period: str = 'month') -> dict:


        return await self.analytics_repository.get_problems_analytics(period)