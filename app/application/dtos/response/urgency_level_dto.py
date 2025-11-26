
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UrgencyEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class UrgencyLevelDto(BaseModel):

    level: UrgencyEnum = Field(
        ...,
        description="Nivel de urgencia",
        example="HIGH"
    )
    
    description: str = Field(
        ...,
        max_length=500,
        description="Descripción del nivel de urgencia",
        example="Atender en 1-3 días. Problema grave que puede empeorar rápidamente."
    )
    
    safe_to_drive: bool = Field(
        ...,
        description="¿Es seguro seguir conduciendo?",
        example=True
    )
    
    max_mileage_recommended: Optional[int] = Field(
        default=None,
        ge=0,
        description="Kilometraje máximo recomendado antes de reparar",
        example=500
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": "HIGH",
                "description": "Atender en 1-3 días. Problema grave que puede empeorar.",
                "safe_to_drive": True,
                "max_mileage_recommended": 500
            }
        }