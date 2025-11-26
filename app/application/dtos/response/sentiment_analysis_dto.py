
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, Dict, Any
from .sentiment_result_dto import SentimentResultDto


class SentimentAnalysisDto(BaseModel):

    id: UUID4 = Field(
        ...,
        description="ID del análisis",
        example="654e3210-f98g-76h5-i432-109876543210"
    )
    
    text: str = Field(
        ...,
        max_length=5000,
        description="Texto analizado",
        example="El servicio fue excelente, muy profesionales y rápidos"
    )
    
    sentiment: SentimentResultDto = Field(
        ...,
        description="Resultado del análisis de sentimiento"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto opcional del análisis"
    )
    
    analyzed_at: datetime = Field(
        ...,
        description="Fecha y hora del análisis",
        example="2024-11-25T10:20:00Z"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "654e3210-f98g-76h5-i432-109876543210",
                "text": "El servicio fue excelente, muy profesionales y rápidos",
                "sentiment": {
                    "label": "POSITIVE",
                    "score": 0.94,
                    "scores": {
                        "positive": 0.94,
                        "neutral": 0.04,
                        "negative": 0.02
                    }
                },
                "context": {
                    "review_id": "123e4567-e89b-12d3-a456-426614174000",
                    "workshop_id": "987e6543-e21b-12d3-a456-426614174999"
                },
                "analyzed_at": "2024-11-25T10:20:00Z"
            }
        }