
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..value_objects import (
    MessageId,
    MessageRole,
    MessageContent,
    AttachmentType,
)
from ..exceptions import (
    InvalidMessageContentException,
    TooManyAttachmentsException,
)


class Attachment:
    
    MAX_ATTACHMENTS = 3
    
    def __init__(
        self,
        attachment_type: AttachmentType,
        url: str,
    ):
        self._type = attachment_type
        self._url = url
    
    @property
    def type(self) -> AttachmentType:
        return self._type
    
    @property
    def url(self) -> str:
        return self._url
    
    def to_dict(self) -> dict:
        return {
            "type": self._type.value,
            "url": self._url,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Attachment":
        return Attachment(
            attachment_type=AttachmentType(data["type"]),
            url=data["url"],
        )


class DiagnosisMessage:

    
    def __init__(
        self,
        message_id: MessageId,
        session_id: UUID,
        role: MessageRole,
        content: MessageContent,
        attachments: Optional[list[Attachment]] = None,
        timestamp: Optional[datetime] = None,
    ):
        self._message_id = message_id
        self._session_id = session_id
        self._role = role
        self._content = content
        self._attachments = attachments or []
        self._timestamp = timestamp or datetime.utcnow()
        
        if len(self._attachments) > Attachment.MAX_ATTACHMENTS:
            raise TooManyAttachmentsException(
                max_allowed=Attachment.MAX_ATTACHMENTS,
                provided=len(self._attachments),
            )
    
    @staticmethod
    def create(
        session_id: UUID,
        role: MessageRole,
        content: str,
        attachments: Optional[list[dict]] = None,
    ) -> "DiagnosisMessage":
        
        message_id = MessageId.generate()
        message_content = MessageContent(content)
        
        attachment_objects = []
        if attachments:
            for att in attachments:
                attachment_objects.append(Attachment.from_dict(att))
        
        return DiagnosisMessage(
            message_id=message_id,
            session_id=session_id,
            role=role,
            content=message_content,
            attachments=attachment_objects,
        )
    
    
    @property
    def id(self) -> MessageId:
        return self._message_id
    
    @property
    def session_id(self) -> UUID:
        return self._session_id
    
    @property
    def role(self) -> MessageRole:
        return self._role
    
    @property
    def content(self) -> MessageContent:
        return self._content
    
    @property
    def attachments(self) -> list[Attachment]:
        return self._attachments.copy()
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    def is_user_message(self) -> bool:
        return self._role.is_user()
    
    def is_assistant_message(self) -> bool:
        return self._role.is_assistant()
    
    def has_attachments(self) -> bool:
        return len(self._attachments) > 0
    
    def to_dict(self) -> dict:
        return {
            "id": str(self._message_id.value),
            "session_id": str(self._session_id),
            "role": self._role.value,
            "content": self._content.value,
            "attachments": [att.to_dict() for att in self._attachments],
            "timestamp": self._timestamp.isoformat(),
        }
    
    @staticmethod
    def from_primitives(
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        attachments: list[dict],
        timestamp: datetime,
    ) -> "DiagnosisMessage":
        
        attachment_objects = [
            Attachment.from_dict(att) for att in attachments
        ]
        
        return DiagnosisMessage(
            message_id=MessageId(UUID(message_id)),
            session_id=UUID(session_id),
            role=MessageRole(role),
            content=MessageContent(content),
            attachments=attachment_objects,
            timestamp=timestamp,
        )