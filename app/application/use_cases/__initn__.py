"""
Use Cases del Diagnosis Service.
Casos de uso organizados por funcionalidad.
"""

from .diagnosis_session import *
from .classification import *
from .recommendations import *
from .sentiment import *
from .analytics import *

__all__ = [
    'StartDiagnosisSessionUseCase',
    'GetUserSessionsUseCase',
    'GetSessionByIdUseCase',
    'GetSessionMessagesUseCase',
    'SendMessageUseCase',
    
    
    'ClassifyProblemUseCase',
    'GetUrgencyLevelUseCase',
    'GetCostEstimateUseCase',
    
    
    'GetWorkshopRecommendationsUseCase',
    
    
    'AnalyzeSentimentUseCase',
    'BatchAnalyzeSentimentUseCase',
    
    'GetAnalyticsDashboardUseCase',
    'GetProblemsAnalyticsUseCase',
    'GetWorkshopsPerformanceUseCase',
    'GetMLModelsMetricsUseCase',
    'GenerateCustomReportUseCase',
    
    
    'VehicleNotFoundException',
    'VehicleNotOwnedByUserException',
    'SessionNotFoundException',
    'SessionNotOwnedByUserException',
    'SessionNotActiveException',
    'InsufficientDataException',
    'ClassificationNotFoundException',
    'BatchSizeTooLargeException',
]