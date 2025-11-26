
from uuid import UUID
from typing import Protocol

from app.domain.entities.problem_classification import ProblemClassification
from app.domain.value_objects import SessionId, CostEstimate, Currency
from app.application.dtos.response import CostEstimateDto, CostBreakdownDto


class ProblemClassificationRepository(Protocol):
    
    async def find_by_session_id(self, session_id: SessionId) -> ProblemClassification | None:
        ...


class CostEstimatorService(Protocol):
    
    async def estimate_cost(
        self,
        category: str,
        symptoms: list[str]
    ) -> dict:

        ...


class GetCostEstimateUseCase:

    
    def __init__(
        self,
        classification_repository: ProblemClassificationRepository,
        cost_estimator: CostEstimatorService
    ):
        self.classification_repository = classification_repository
        self.cost_estimator = cost_estimator
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> CostEstimateDto:

        session_id_vo = SessionId.from_string(str(session_id))
        classification = await self.classification_repository.find_by_session_id(session_id_vo)
        
        if not classification:
            raise ClassificationNotFoundException(
                f"Clasificación no encontrada para la sesión {session_id}. Por favor clasifique primero."
            )
        
        cost_result = await self.cost_estimator.estimate_cost(
            category=classification.get_category().value,
            symptoms=classification.get_symptoms()
        )
        
        cost_estimate = CostEstimate.create(
            min_cost=cost_result['min_cost'],
            max_cost=cost_result['max_cost'],
            currency=Currency.MXN
        )
        
        breakdown = None
        if 'breakdown' in cost_result:
            bd = cost_result['breakdown']
            breakdown = CostBreakdownDto(
                parts_min=bd['parts_min'],
                parts_max=bd['parts_max'],
                labor_min=bd['labor_min'],
                labor_max=bd['labor_max']
            )
        
        return CostEstimateDto(
            min_cost=cost_estimate.min_cost,
            max_cost=cost_estimate.max_cost,
            currency=cost_estimate.currency.value,
            breakdown=breakdown,
            disclaimer="Esta es una estimación aproximada. El costo final puede variar según el taller."
        )


class ClassificationNotFoundException(Exception):
    """No existe clasificación para la sesión."""
    pass