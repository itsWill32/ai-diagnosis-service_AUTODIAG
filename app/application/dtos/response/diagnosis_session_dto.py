
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional
from enum import Enum


class SessionStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class DiagnosisSessionDto(BaseModel):

    id: UUID4 = Field(
        ...,
        description="ID de la sesión",
        example="456e7890-e12b-34c5-d678-426614174111"
    )
    
    user_id: UUID4 = Field(
        ...,
        description="ID del usuario",
        example="789e0123-e45b-67c8-d901-234567890abc"
    )
    
    vehicle_id: UUID4 = Field(
        ...,
        description="ID del vehículo",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    status: SessionStatusEnum = Field(
        ...,
        description="Estado de la sesión"
    )
    
    started_at: datetime = Field(
        ...,
        description="Fecha y hora de inicio",
        example="2024-11-25T10:00:00Z"
    )
    
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de finalización",
        example="2024-11-25T10:30:00Z"
    )
    
    messages_count: int = Field(
        ...,
        ge=0,
        description="Número de mensajes en la sesión",
        example=8
    )
    
    summary: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Resumen del diagnóstico",
        example="Problema identificado en sistema de frenos"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "456e7890-e12b-34c5-d678-426614174111",
                "user_id": "789e0123-e45b-67c8-d901-234567890abc",
                "vehicle_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "ACTIVE",
                "started_at": "2024-11-25T10:00:00Z",
                "completed_at": None,
                "messages_count": 8,
                "summary": None
            }
        }