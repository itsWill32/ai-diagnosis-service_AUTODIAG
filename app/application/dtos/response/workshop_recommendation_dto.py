
from pydantic import BaseModel, Field, UUID4
from typing import List


class WorkshopRecommendationDto(BaseModel):

    workshop_id: UUID4 = Field(
        ...,
        description="ID del taller",
        example="987e6543-e21b-12d3-a456-426614174999"
    )
    
    workshop_name: str = Field(
        ...,
        max_length=200,
        description="Nombre del taller",
        example="Taller Mecánico El Rayo"
    )
    
    match_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Qué tan bien coincide con el problema (0-1)",
        example=0.92
    )
    
    reasons: List[str] = Field(
        ...,
        description="Razones de la recomendación",
        example=[
            "Especializado en sistemas de frenos",
            "Excelente calificación (4.8/5)",
            "Cerca de tu ubicación (2.3 km)"
        ]
    )
    
    distance_km: float = Field(
        ...,
        ge=0.0,
        description="Distancia en kilómetros",
        example=2.3
    )
    
    rating: float = Field(
        ...,
        ge=0.0,
        le=5.0,
        description="Calificación promedio del taller",
        example=4.8
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "workshop_id": "987e6543-e21b-12d3-a456-426614174999",
                "workshop_name": "Taller Mecánico El Rayo",
                "match_score": 0.92,
                "reasons": [
                    "Especializado en sistemas de frenos",
                    "Excelente calificación (4.8/5)",
                    "Cerca de tu ubicación (2.3 km)"
                ],
                "distance_km": 2.3,
                "rating": 4.8
            }
        }