
from uuid import UUID
from typing import Protocol, List, Optional

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.value_objects import UserId, VehicleId
from app.application.dtos.response import DiagnosisSessionDto


class DiagnosisSessionRepository(Protocol):
    
    async def find_by_user_id(
        self,
        user_id: UserId,
        vehicle_id: Optional[VehicleId] = None,
        limit: int = 10
    ) -> List[DiagnosisSession]:
        ...


class GetUserSessionsUseCase:

    
    def __init__(self, session_repository: DiagnosisSessionRepository):
        self.session_repository = session_repository
    
    async def execute(
        self,
        user_id: UUID,
        vehicle_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[DiagnosisSessionDto]:

        user_id_vo = UserId.from_string(str(user_id))
        vehicle_id_vo = VehicleId.from_string(str(vehicle_id)) if vehicle_id else None
        
        sessions = await self.session_repository.find_by_user_id(
            user_id=user_id_vo,
            vehicle_id=vehicle_id_vo,
            limit=limit
        )
        
        return [self._to_dto(session) for session in sessions]
    
    def _to_dto(self, session: DiagnosisSession) -> DiagnosisSessionDto:
        return DiagnosisSessionDto(
            id=UUID(session.get_id().to_string()),
            user_id=UUID(session.get_user_id().to_string()),
            vehicle_id=UUID(session.get_vehicle_id().to_string()),
            status=session.get_status().value,
            started_at=session.get_started_at(),
            completed_at=session.get_completed_at(),
            messages_count=session.get_messages_count(),
            summary=session.get_summary()
        )