
from pydantic import BaseModel, Field, UUID4, HttpUrl
from datetime import datetime
from typing import List, Optional
from enum import Enum


class MessageRoleEnum(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class AttachmentTypeEnum(str, Enum):
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


class AttachmentResponseDto(BaseModel):
    type: AttachmentTypeEnum
    url: HttpUrl


class DiagnosisMessageDto(BaseModel):

    id: UUID4 = Field(
        ...,
        description="ID del mensaje",
        example="789e0123-e45b-67c8-d901-234567890abc"
    )
    
    session_id: UUID4 = Field(
        ...,
        description="ID de la sesión",
        example="456e7890-e12b-34c5-d678-426614174111"
    )
    
    role: MessageRoleEnum = Field(
        ...,
        description="Rol del mensaje (USER o ASSISTANT)"
    )
    
    content: str = Field(
        ...,
        max_length=2000,
        description="Contenido del mensaje",
        example="Mi auto hace un ruido extraño al frenar"
    )
    
    attachments: Optional[List[AttachmentResponseDto]] = Field(
        default=None,
        description="Archivos adjuntos"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Fecha y hora del mensaje",
        example="2024-11-25T10:05:00Z"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "789e0123-e45b-67c8-d901-234567890abc",
                "session_id": "456e7890-e12b-34c5-d678-426614174111",
                "role": "USER",
                "content": "Mi auto hace un ruido extraño al frenar",
                "attachments": None,
                "timestamp": "2024-11-25T10:05:00Z"
            }
        }