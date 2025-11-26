
from pydantic import BaseModel, Field
from enum import Enum


class SentimentLabelEnum(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class SentimentScoresDto(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0, description="Score positivo")
    neutral: float = Field(..., ge=0.0, le=1.0, description="Score neutral")
    negative: float = Field(..., ge=0.0, le=1.0, description="Score negativo")


class SentimentResultDto(BaseModel):

    label: SentimentLabelEnum = Field(
        ...,
        description="Etiqueta del sentimiento",
        example="POSITIVE"
    )
    
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza del análisis (0-1)",
        example=0.94
    )
    
    scores: SentimentScoresDto = Field(
        ...,
        description="Scores individuales por sentimiento"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "POSITIVE",
                "score": 0.94,
                "scores": {
                    "positive": 0.94,
                    "neutral": 0.04,
                    "negative": 0.02
                }
            }
        }