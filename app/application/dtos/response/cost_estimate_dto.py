
from pydantic import BaseModel, Field
from typing import Optional


class CostBreakdownDto(BaseModel):
    parts_min: float = Field(..., ge=0, description="Costo mínimo de refacciones")
    parts_max: float = Field(..., ge=0, description="Costo máximo de refacciones")
    labor_min: float = Field(..., ge=0, description="Costo mínimo de mano de obra")
    labor_max: float = Field(..., ge=0, description="Costo máximo de mano de obra")


class CostEstimateDto(BaseModel):

    min_cost: float = Field(
        ...,
        ge=0,
        description="Costo mínimo estimado",
        example=800.0
    )
    
    max_cost: float = Field(
        ...,
        ge=0,
        description="Costo máximo estimado",
        example=1500.0
    )
    
    currency: str = Field(
        default="MXN",
        description="Moneda de la estimación",
        example="MXN"
    )
    
    breakdown: Optional[CostBreakdownDto] = Field(
        default=None,
        description="Desglose de costos por categoría"
    )
    
    disclaimer: str = Field(
        default="Esta es una estimación aproximada. El costo final puede variar según el taller.",
        max_length=500,
        description="Aviso legal sobre la estimación"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "min_cost": 800.0,
                "max_cost": 1500.0,
                "currency": "MXN",
                "breakdown": {
                    "parts_min": 500.0,
                    "parts_max": 900.0,
                    "labor_min": 300.0,
                    "labor_max": 600.0
                },
                "disclaimer": "Esta es una estimación aproximada. El costo final puede variar según el taller."
            }
        }