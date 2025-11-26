
from uuid import UUID
from typing import Protocol

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.value_objects import SessionId, UserId
from app.application.dtos.response import DiagnosisSessionDto


class DiagnosisSessionRepository(Protocol):
    
    async def find_by_id(self, session_id: SessionId) -> DiagnosisSession | None:
        ...


class GetSessionByIdUseCase:

    
    def __init__(self, session_repository: DiagnosisSessionRepository):
        self.session_repository = session_repository
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> DiagnosisSessionDto:

        session_id_vo = SessionId.from_string(str(session_id))
        session = await self.session_repository.find_by_id(session_id_vo)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        if session.get_user_id().to_string() != str(user_id):
            raise SessionNotOwnedByUserException(
                f"Session {session_id} no pertenece al usuario {user_id}"
            )
        
        return self._to_dto(session)
    
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


class SessionNotFoundException(Exception):
    """La sesión no existe."""
    pass


class SessionNotOwnedByUserException(Exception):
    """La sesión no pertenece al usuario."""
    pass