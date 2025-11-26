
from typing import Protocol


class AnalyticsRepository(Protocol):
    
    async def get_ml_models_metrics(self) -> dict:
        ...


class GetMLModelsMetricsUseCase:
    
    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
    
    async def execute(self) -> dict:

        return await self.analytics_repository.get_ml_models_metrics()