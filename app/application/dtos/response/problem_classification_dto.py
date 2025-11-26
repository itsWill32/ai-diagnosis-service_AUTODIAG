
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import List, Optional


class ProblemClassificationDto(BaseModel):

    id: UUID4 = Field(
        ...,
        description="ID de la clasificación",
        example="321f5678-g90h-12i3-j456-789012345678"
    )
    
    session_id: UUID4 = Field(
        ...,
        description="ID de la sesión de diagnóstico",
        example="456e7890-e12b-34c5-d678-426614174111"
    )
    
    category: str = Field(
        ...,
        description="Categoría del problema",
        example="BRAKES"
    )
    
    subcategory: Optional[str] = Field(
        default=None,
        description="Subcategoría específica",
        example="Worn brake pads"
    )
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza de la clasificación (0-1)",
        example=0.87
    )
    
    symptoms: List[str] = Field(
        ...,
        description="Lista de síntomas identificados",
        example=[
            "Chirrido metálico al frenar",
            "Vibración en el pedal",
            "Mayor distancia de frenado"
        ]
    )
    
    created_at: datetime = Field(
        ...,
        description="Fecha de clasificación",
        example="2024-11-25T10:15:00Z"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "321f5678-g90h-12i3-j456-789012345678",
                "session_id": "456e7890-e12b-34c5-d678-426614174111",
                "category": "BRAKES",
                "subcategory": "Worn brake pads",
                "confidence_score": 0.87,
                "symptoms": [
                    "Chirrido metálico al frenar",
                    "Vibración en el pedal"
                ],
                "created_at": "2024-11-25T10:15:00Z"
            }
        }