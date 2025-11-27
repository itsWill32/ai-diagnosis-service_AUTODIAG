
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from ..value_objects import SessionId, MessageRole
from ..exceptions import (
    SessionNotActiveException,
    InvalidSessionStatusException,
    InsufficientMessagesException,
)
from .diagnosis_message import DiagnosisMessage


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class DiagnosisSession:

    
    MIN_MESSAGES_FOR_CLASSIFICATION = 2
    
    def __init__(
        self,
        session_id: SessionId,
        user_id: UUID,
        vehicle_id: UUID,
        status: SessionStatus,
        messages: list[DiagnosisMessage],
        summary: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self._session_id = session_id
        self._user_id = user_id
        self._vehicle_id = vehicle_id
        self._status = status
        self._messages = messages
        self._summary = summary
        self._started_at = started_at or datetime.utcnow()
        self._completed_at = completed_at
    
    @staticmethod
    def create(
        user_id: UUID,
        vehicle_id: UUID,
        initial_message: str,
    ) -> "DiagnosisSession":
        """Factory method para crear una nueva sesión"""
        
        session_id = SessionId.generate()
        
        first_message = DiagnosisMessage.create(
            session_id=session_id.value,
            role=MessageRole.user(),
            content=initial_message,
        )
        
        return DiagnosisSession(
            session_id=session_id,
            user_id=user_id,
            vehicle_id=vehicle_id,
            status=SessionStatus.ACTIVE,
            messages=[first_message],
        )
    
    
    @property
    def id(self) -> SessionId:
        return self._session_id
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    @property
    def vehicle_id(self) -> UUID:
        return self._vehicle_id
    
    @property
    def status(self) -> SessionStatus:
        return self._status
    
    @property
    def messages(self) -> list[DiagnosisMessage]:
        return self._messages.copy()
    
    @property
    def summary(self) -> Optional[str]:
        return self._summary
    
    @property
    def started_at(self) -> datetime:
        return self._started_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    
    def add_message(self, message: DiagnosisMessage) -> None:
        
        if not self.is_active():
            raise SessionNotActiveException(
                session_id=str(self._session_id.value),
                current_status=self._status.value,
            )
        
        self._messages.append(message)
    
    def complete(self, summary: Optional[str] = None) -> None:
        
        if self._status != SessionStatus.ACTIVE:
            raise InvalidSessionStatusException(
                current_status=self._status.value,
                target_status=SessionStatus.COMPLETED.value,
            )
        
        self._status = SessionStatus.COMPLETED
        self._summary = summary
        self._completed_at = datetime.utcnow()
    
    def abandon(self) -> None:
        
        if self._status != SessionStatus.ACTIVE:
            raise InvalidSessionStatusException(
                current_status=self._status.value,
                target_status=SessionStatus.ABANDONED.value,
            )
        
        self._status = SessionStatus.ABANDONED
        self._completed_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        return self._status == SessionStatus.ACTIVE
    
    def is_completed(self) -> bool:
        return self._status == SessionStatus.COMPLETED
    
    def is_abandoned(self) -> bool:
        return self._status == SessionStatus.ABANDONED
    
    def get_messages_count(self) -> int:
        return len(self._messages)
    
    def get_user_messages(self) -> list[DiagnosisMessage]:
        return [msg for msg in self._messages if msg.is_user_message()]
    
    def get_assistant_messages(self) -> list[DiagnosisMessage]:
        return [msg for msg in self._messages if msg.is_assistant_message()]
    
    def has_enough_messages_for_classification(self) -> bool:
        return len(self.get_user_messages()) >= self.MIN_MESSAGES_FOR_CLASSIFICATION
    
    def validate_can_classify(self) -> None:
        
        if not self.has_enough_messages_for_classification():
            raise InsufficientMessagesException(
                session_id=str(self._session_id.value),
                required=self.MIN_MESSAGES_FOR_CLASSIFICATION,
                actual=len(self.get_user_messages()),
            )
    
    def get_conversation_text(self) -> str:
        
        texts = []
        for message in self._messages:
            role_prefix = "Usuario" if message.is_user_message() else "Asistente"
            texts.append(f"{role_prefix}: {message.content.value}")
        
        return "\n".join(texts)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self._session_id.value),
            "user_id": str(self._user_id),
            "vehicle_id": str(self._vehicle_id),
            "status": self._status.value,
            "messages_count": len(self._messages),
            "summary": self._summary,
            "started_at": self._started_at.isoformat(),
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
        }
    
    @staticmethod
    def from_primitives(
        session_id: str,
        user_id: str,
        vehicle_id: str,
        status: str,
        messages: list[DiagnosisMessage],
        summary: Optional[str],
        started_at: datetime,
        completed_at: Optional[datetime],
    ) -> "DiagnosisSession":
        """Reconstruye la entidad desde primitivos"""
        
        return DiagnosisSession(
            session_id=SessionId(UUID(session_id)),
            user_id=UUID(user_id),
            vehicle_id=UUID(vehicle_id),
            status=SessionStatus(status),
            messages=messages,
            summary=summary,
            started_at=started_at,
            completed_at=completed_at,
        )