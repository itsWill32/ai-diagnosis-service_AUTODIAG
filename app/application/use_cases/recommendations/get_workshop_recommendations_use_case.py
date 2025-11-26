
from uuid import UUID
from typing import Protocol, List

from app.domain.entities.problem_classification import ProblemClassification
from app.domain.value_objects import SessionId, WorkshopId
from app.application.dtos.response import WorkshopRecommendationDto


class ProblemClassificationRepository(Protocol):
    
    async def find_by_session_id(self, session_id: SessionId) -> ProblemClassification | None:
        ...


class WorkshopRecommenderService(Protocol):
    """Servicio ML para recomendar talleres."""
    
    async def recommend_workshops(
        self,
        category: str,
        user_location: dict,
        limit: int = 3
    ) -> List[dict]:

        ...


class WorkshopServiceClient(Protocol):
    
    async def get_workshop_details(self, workshop_id: UUID) -> dict:
        ...


class GetWorkshopRecommendationsUseCase:

    
    def __init__(
        self,
        classification_repository: ProblemClassificationRepository,
        recommender_service: WorkshopRecommenderService,
        workshop_client: WorkshopServiceClient
    ):
        self.classification_repository = classification_repository
        self.recommender_service = recommender_service
        self.workshop_client = workshop_client
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID,
        user_location: dict,
        limit: int = 3
    ) -> List[WorkshopRecommendationDto]:

        session_id_vo = SessionId.from_string(str(session_id))
        classification = await self.classification_repository.find_by_session_id(session_id_vo)
        
        if not classification:
            raise ClassificationNotFoundException(
                f"Clasificación no encontrada para la sesión {session_id}. Por favor clasifique primero."
            )
        
        recommendations = await self.recommender_service.recommend_workshops(
            category=classification.get_category().value,
            user_location=user_location,
            limit=limit
        )
        
        enriched_recommendations = []
        
        for rec in recommendations:
            workshop_details = await self.workshop_client.get_workshop_details(
                workshop_id=UUID(rec['workshop_id'])
            )
            
            enriched_recommendations.append(
                WorkshopRecommendationDto(
                    workshop_id=UUID(rec['workshop_id']),
                    workshop_name=workshop_details.get('businessName', 'Taller'),
                    match_score=rec['match_score'],
                    reasons=rec['reasons'],
                    distance_km=rec['distance_km'],
                    rating=rec.get('rating', 0.0)
                )
            )
        
        return enriched_recommendations


class ClassificationNotFoundException(Exception):
    """No existe clasificación para la sesión."""
    pass