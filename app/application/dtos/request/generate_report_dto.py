
from pydantic import BaseModel, Field
from typing import List
from datetime import date
from enum import Enum


class ReportTypeEnum(str, Enum):
    MONTHLY_SUMMARY = "MONTHLY_SUMMARY"
    QUARTERLY_SUMMARY = "QUARTERLY_SUMMARY"
    CUSTOM = "CUSTOM"


class MetricEnum(str, Enum):
    TOTAL_DIAGNOSES = "TOTAL_DIAGNOSES"
    ACCURACY_RATE = "ACCURACY_RATE"
    TOP_PROBLEMS = "TOP_PROBLEMS"
    WORKSHOP_PERFORMANCE = "WORKSHOP_PERFORMANCE"
    SENTIMENT_TRENDS = "SENTIMENT_TRENDS"


class ReportFormatEnum(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    JSON = "JSON"


class GenerateReportDto(BaseModel):

    report_type: ReportTypeEnum = Field(
        ...,
        description="Tipo de reporte a generar"
    )
    
    from_date: date = Field(
        ...,
        description="Fecha inicio del reporte",
        example="2024-10-01"
    )
    
    to_date: date = Field(
        ...,
        description="Fecha fin del reporte",
        example="2024-10-31"
    )
    
    metrics: List[MetricEnum] = Field(
        ...,
        min_length=1,
        description="Métricas a incluir en el reporte",
        example=["TOTAL_DIAGNOSES", "ACCURACY_RATE", "TOP_PROBLEMS"]
    )
    
    format: ReportFormatEnum = Field(
        default=ReportFormatEnum.PDF,
        description="Formato de salida del reporte"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "MONTHLY_SUMMARY",
                "from_date": "2024-10-01",
                "to_date": "2024-10-31",
                "metrics": [
                    "TOTAL_DIAGNOSES",
                    "ACCURACY_RATE",
                    "TOP_PROBLEMS"
                ],
                "format": "PDF"
            }
        }