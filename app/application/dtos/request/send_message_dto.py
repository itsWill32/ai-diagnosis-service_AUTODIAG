
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from enum import Enum


class AttachmentTypeEnum(str, Enum):
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


class AttachmentDto(BaseModel):

    type: AttachmentTypeEnum = Field(
        ...,
        description="Tipo de archivo adjunto"
    )
    
    url: HttpUrl = Field(
        ...,
        description="URL del archivo adjunto",
        example="https://cdn.autodiag.com/audio/recording123.m4a"
    )


class SendMessageDto(BaseModel):

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Contenido del mensaje",
        example="El ruido suena como un chirrido metálico"
    )
    
    attachments: Optional[List[AttachmentDto]] = Field(
        default=None,
        max_length=3,
        description="Archivos adjuntos (máximo 3)",
        example=[
            {
                "type": "AUDIO",
                "url": "https://cdn.autodiag.com/audio/recording123.m4a"
            }
        ]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "El ruido suena como un chirrido metálico",
                "attachments": [
                    {
                        "type": "AUDIO",
                        "url": "https://cdn.autodiag.com/audio/recording123.m4a"
                    }
                ]
            }
        }