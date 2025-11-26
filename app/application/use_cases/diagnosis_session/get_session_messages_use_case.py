
from uuid import UUID
from typing import Protocol, List

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.entities.diagnosis_message import DiagnosisMessage
from app.domain.value_objects import SessionId
from app.application.dtos.response import DiagnosisMessageDto, AttachmentResponseDto


class DiagnosisSessionRepository(Protocol):
    
    async def find_by_id(self, session_id: SessionId) -> DiagnosisSession | None:
        """Busca una sesión por ID."""
        ...


class GetSessionMessagesUseCase:

    
    def __init__(self, session_repository: DiagnosisSessionRepository):
        self.session_repository = session_repository
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> List[DiagnosisMessageDto]:

        session_id_vo = SessionId.from_string(str(session_id))
        session = await self.session_repository.find_by_id(session_id_vo)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        if session.get_user_id().to_string() != str(user_id):
            raise SessionNotOwnedByUserException(
                f"Session {session_id} No pertence al usuario {user_id}"
            )
        
        messages = session.get_messages()
        return [self._to_dto(msg) for msg in messages]
    
    def _to_dto(self, message: DiagnosisMessage) -> DiagnosisMessageDto:
        attachments = None
        if message.get_attachments():
            attachments = [
                AttachmentResponseDto(
                    type=att.get_type().value,
                    url=att.get_url()
                )
                for att in message.get_attachments()
            ]
        
        return DiagnosisMessageDto(
            id=UUID(message.get_id().to_string()),
            session_id=UUID(message.get_session_id().to_string()),
            role=message.get_role().value,
            content=message.get_content().to_string(),
            attachments=attachments,
            timestamp=message.get_timestamp()
        )



class SessionNotFoundException(Exception):
    """La sesión no existe."""
    pass


class SessionNotOwnedByUserException(Exception):
    """La sesión no pertenece al usuario."""
    pass