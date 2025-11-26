
from uuid import UUID
from typing import Protocol

from app.domain.entities.problem_classification import ProblemClassification
from app.domain.value_objects import SessionId, UrgencyLevel
from app.application.dtos.response import UrgencyLevelDto


class ProblemClassificationRepository(Protocol):
    
    async def find_by_session_id(self, session_id: SessionId) -> ProblemClassification | None:
        ...


class UrgencyAnalyzerService(Protocol):
    
    async def analyze_urgency(
        self,
        category: str,
        symptoms: list[str]
    ) -> dict:

        ...


class GetUrgencyLevelUseCase:

    
    def __init__(
        self,
        classification_repository: ProblemClassificationRepository,
        urgency_analyzer: UrgencyAnalyzerService
    ):
        self.classification_repository = classification_repository
        self.urgency_analyzer = urgency_analyzer
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> UrgencyLevelDto:

        session_id_vo = SessionId.from_string(str(session_id))
        classification = await self.classification_repository.find_by_session_id(session_id_vo)
        
        if not classification:
            raise ClassificationNotFoundException(
                f"Clasificacion no encontrada para la sesión {session_id}. Por favor clasifique primero."
            )
        
        urgency_result = await self.urgency_analyzer.analyze_urgency(
            category=classification.get_category().value,
            symptoms=classification.get_symptoms()
        )
        
        level = urgency_result['level'].upper()
        
        if level == 'CRITICAL':
            urgency = UrgencyLevel.create_critical(
                description=urgency_result['description']
            )
        elif level == 'HIGH':
            urgency = UrgencyLevel.create_high(
                description=urgency_result['description'],
                max_mileage=urgency_result.get('max_mileage')
            )
        elif level == 'MEDIUM':
            urgency = UrgencyLevel.create_medium(
                description=urgency_result['description'],
                max_mileage=urgency_result.get('max_mileage')
            )
        else: 
            urgency = UrgencyLevel.create_low(
                description=urgency_result['description']
            )
        
        return self._to_dto(urgency)
    
    def _to_dto(self, urgency: UrgencyLevel) -> UrgencyLevelDto:
        return UrgencyLevelDto(
            level=urgency.level.value,
            description=urgency.description,
            safe_to_drive=urgency.safe_to_drive,
            max_mileage_recommended=urgency.max_mileage_recommended
        )


class ClassificationNotFoundException(Exception):
    """No existe clasificación para la sesión."""
    pass