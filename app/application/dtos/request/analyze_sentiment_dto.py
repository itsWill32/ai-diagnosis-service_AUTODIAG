
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any


class AnalyzeSentimentDto(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texto a analizar",
        example="El servicio fue excelente, muy profesionales y rápidos"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto opcional del análisis",
        example={
            "review_id": "123e4567-e89b-12d3-a456-426614174000",
            "workshop_id": "987e6543-e21b-12d3-a456-426614174999"
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "El servicio fue excelente, muy profesionales y rápidos",
                "context": {
                    "review_id": "123e4567-e89b-12d3-a456-426614174000",
                    "workshop_id": "987e6543-e21b-12d3-a456-426614174999"
                }
            }
        }