
from datetime import date
from typing import Protocol

from app.application.dtos.response import (
    AnalyticsDashboardDto,
    PeriodDto,
    TotalsDto,
    TrendsDto,
    TopProblemDto
)


class AnalyticsRepository(Protocol):
    
    async def get_totals(self, from_date: date, to_date: date) -> dict:
        ...
    
    async def get_trends(self, from_date: date, to_date: date) -> dict:
        ...
    
    async def get_top_problems(self, from_date: date, to_date: date, limit: int = 10) -> list:
        ...


class GetAnalyticsDashboardUseCase:

    
    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
    
    async def execute(
        self,
        from_date: date,
        to_date: date
    ) -> AnalyticsDashboardDto:

        totals_data = await self.analytics_repository.get_totals(from_date, to_date)
        trends_data = await self.analytics_repository.get_trends(from_date, to_date)
        top_problems_data = await self.analytics_repository.get_top_problems(
            from_date, to_date, limit=10
        )
        
        period = PeriodDto(from_date=from_date, to_date=to_date)
        
        totals = TotalsDto(
            total_diagnoses=totals_data['total_diagnoses'],
            total_users=totals_data['total_users'],
            total_workshops=totals_data['total_workshops'],
            total_appointments=totals_data['total_appointments']
        )
        
        trends = TrendsDto(
            diagnoses_growth=trends_data['diagnoses_growth'],
            avg_response_time=trends_data['avg_response_time']
        )
        
        top_problems = [
            TopProblemDto(category=item['category'], count=item['count'])
            for item in top_problems_data
        ]
        
        return AnalyticsDashboardDto(
            period=period,
            totals=totals,
            trends=trends,
            top_problems=top_problems
        )