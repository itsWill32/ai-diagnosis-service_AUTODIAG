
from pydantic import BaseModel, Field
from datetime import date
from typing import List


class PeriodDto(BaseModel):
    from_date: date = Field(..., description="Fecha inicio")
    to_date: date = Field(..., description="Fecha fin")


class TotalsDto(BaseModel):
    total_diagnoses: int = Field(..., ge=0, description="Total de diagnósticos")
    total_users: int = Field(..., ge=0, description="Total de usuarios")
    total_workshops: int = Field(..., ge=0, description="Total de talleres")
    total_appointments: int = Field(..., ge=0, description="Total de citas")


class TrendsDto(BaseModel):
    diagnoses_growth: float = Field(..., description="% de crecimiento en diagnósticos")
    avg_response_time: float = Field(..., ge=0, description="Tiempo promedio de respuesta (segundos)")


class TopProblemDto(BaseModel):
    category: str = Field(..., description="Categoría del problema")
    count: int = Field(..., ge=0, description="Cantidad de ocurrencias")


class AnalyticsDashboardDto(BaseModel):

    period: PeriodDto = Field(
        ...,
        description="Período del reporte"
    )
    
    totals: TotalsDto = Field(
        ...,
        description="Totales generales del sistema"
    )
    
    trends: TrendsDto = Field(
        ...,
        description="Tendencias y métricas clave"
    )
    
    top_problems: List[TopProblemDto] = Field(
        ...,
        max_length=10,
        description="Top 10 problemas más comunes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": {
                    "from_date": "2024-10-01",
                    "to_date": "2024-10-31"
                },
                "totals": {
                    "total_diagnoses": 1250,
                    "total_users": 850,
                    "total_workshops": 45,
                    "total_appointments": 620
                },
                "trends": {
                    "diagnoses_growth": 15.3,
                    "avg_response_time": 2.4
                },
                "top_problems": [
                    {"category": "BRAKES", "count": 320},
                    {"category": "ENGINE", "count": 280},
                    {"category": "ELECTRICAL", "count": 195}
                ]
            }
        }