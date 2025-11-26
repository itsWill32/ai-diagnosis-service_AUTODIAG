
from uuid import UUID
from typing import Protocol, List

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.entities.diagnosis_message import DiagnosisMessage
from app.domain.value_objects import (
    SessionId,
    MessageContent,
    AttachmentUrl
)
from app.application.dtos.request import SendMessageDto
from app.application.dtos.response import ChatResponseDto, DiagnosisMessageDto, AttachmentResponseDto


class DiagnosisSessionRepository(Protocol):
    
    async def find_by_id(self, session_id: SessionId) -> DiagnosisSession | None:
        ...
    
    async def save(self, session: DiagnosisSession) -> DiagnosisSession:
        ...


class GeminiChatService(Protocol):
    
    async def send_message(
        self,
        message: str,
        conversation_history: List[dict],
        attachments: List[str] = None
    ) -> dict:

        ...


class SendMessageUseCase:

    
    def __init__(
        self,
        session_repository: DiagnosisSessionRepository,
        gemini_service: GeminiChatService
    ):
        self.session_repository = session_repository
        self.gemini_service = gemini_service
    
    async def execute(
        self,
        session_id: UUID,
        dto: SendMessageDto,
        user_id: UUID
    ) -> ChatResponseDto:

        session_id_vo = SessionId.from_string(str(session_id))
        session = await self.session_repository.find_by_id(session_id_vo)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        if session.get_user_id().to_string() != str(user_id):
            raise SessionNotOwnedByUserException(
                f"Session {session_id} No pertenece al usuario {user_id}"
            )
        
        if not session.is_active():
            raise SessionNotActiveException(
                f"Session {session_id} no está activa (estado: {session.get_status().value})"
            )
        
        user_message = DiagnosisMessage.create_user_message(
            session_id=session.get_id(),
            content=MessageContent.create(dto.content)
        )
        
        if dto.attachments:
            for att_dto in dto.attachments:
                attachment = AttachmentUrl.create(
                    url=str(att_dto.url),
                    attachment_type=att_dto.type.value
                )
                user_message.add_attachment(attachment)
        
        session.add_message(user_message)
        
        conversation_history = self._build_conversation_history(session)
        
        attachment_urls = [str(att.url) for att in (dto.attachments or [])]
        ai_response = await self.gemini_service.send_message(
            message=dto.content,
            conversation_history=conversation_history,
            attachments=attachment_urls if attachment_urls else None
        )
        
        assistant_message = DiagnosisMessage.create_assistant_message(
            session_id=session.get_id(),
            content=MessageContent.create(ai_response['response'])
        )
        
        session.add_message(assistant_message)
        
        await self.session_repository.save(session)
        
        return ChatResponseDto(
            user_message=self._message_to_dto(user_message),
            assistant_message=self._message_to_dto(assistant_message),
            suggested_questions=ai_response.get('suggested_questions', [])
        )
    
    def _build_conversation_history(self, session: DiagnosisSession) -> List[dict]:
        messages = session.get_messages()
        return [
            {
                'role': msg.get_role().value.lower(), 
                'content': msg.get_content().to_string()
            }
            for msg in messages
        ]
    
    def _message_to_dto(self, message: DiagnosisMessage) -> DiagnosisMessageDto:
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


class SessionNotActiveException(Exception):
    """La sesión no está activa."""
    pass