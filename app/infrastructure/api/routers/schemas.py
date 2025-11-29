
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class ProblemCategoryEnum(str, Enum):
    ENGINE = "ENGINE"
    TRANSMISSION = "TRANSMISSION"
    BRAKES = "BRAKES"
    ELECTRICAL = "ELECTRICAL"
    AIR_CONDITIONING = "AIR_CONDITIONING"
    SUSPENSION = "SUSPENSION"
    EXHAUST = "EXHAUST"
    FUEL_SYSTEM = "FUEL_SYSTEM"
    COOLING_SYSTEM = "COOLING_SYSTEM"
    TIRES = "TIRES"
    BATTERY = "BATTERY"
    LIGHTS = "LIGHTS"
    OTHER = "OTHER"


class UrgencyLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SentimentLabelEnum(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"





class StartSessionRequest(BaseModel):
    vehicleId: str = Field(..., description="UUID del vehículo")
    initialMessage: str = Field(..., min_length=10, max_length=1000, description="Descripción inicial del problema")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicleId": "123e4567-e89b-12d3-a456-426614174000",
                "initialMessage": "Mi auto hace un ruido extraño al frenar"
            }
        }


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Contenido del mensaje")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "El ruido suena como un chirrido metálico"
            }
        }


class MessageResponse(BaseModel):
    id: str
    sessionId: str
    role: MessageRole
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SuggestedQuestionsResponse(BaseModel):
    questions: List[str] = Field(..., max_items=3)


class ChatResponse(BaseModel):
    userMessage: MessageResponse
    assistantMessage: MessageResponse
    suggestedQuestions: List[str] = Field(default=[], max_items=3)


class SessionResponse(BaseModel):
    id: str
    userId: str
    vehicleId: str
    status: SessionStatus
    startedAt: datetime
    completedAt: Optional[datetime] = None
    messagesCount: int
    summary: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    id: str
    userId: str
    vehicleId: str
    status: SessionStatus
    startedAt: datetime
    completedAt: Optional[datetime] = None
    messagesCount: int
    summary: Optional[str] = None
    classification: Optional[Dict[str, Any]] = None
    urgency: Optional[Dict[str, Any]] = None
    costEstimate: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True




class ClassificationResponse(BaseModel):
    id: str
    sessionId: str
    category: ProblemCategoryEnum
    subcategory: Optional[str] = None
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza (0-1)")
    symptoms: List[str] = []
    createdAt: datetime
    
    class Config:
        from_attributes = True


class UrgencyResponse(BaseModel):
    level: UrgencyLevelEnum
    description: str
    safeToDriver: bool = Field(..., description="¿Es seguro seguir conduciendo?")
    maxMileageRecommended: Optional[int] = Field(None, description="Kilometraje máximo seguro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": "CRITICAL",
                "description": "NO CONDUCIR - Problema crítico de frenos",
                "safeToDriver": False,
                "maxMileageRecommended": 0
            }
        }


class CostBreakdown(BaseModel):
    partsMin: float
    partsMax: float
    laborMin: float
    laborMax: float


class CostEstimateResponse(BaseModel):
    minCost: float
    maxCost: float
    currency: str = "MXN"
    breakdown: CostBreakdown
    disclaimer: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "minCost": 1320.0,
                "maxCost": 2530.0,
                "currency": "MXN",
                "breakdown": {
                    "partsMin": 880.0,
                    "partsMax": 1650.0,
                    "laborMin": 440.0,
                    "laborMax": 880.0
                },
                "disclaimer": "Esta es una estimación aproximada..."
            }
        }




class WorkshopRecommendationResponse(BaseModel):
    workshopId: str
    workshopName: str
    matchScore: float = Field(..., ge=0.0, le=1.0, description="Qué tan bien coincide (0-1)")
    reasons: List[str] = Field(..., description="Razones de la recomendación")
    distanceKm: float
    rating: float = Field(..., ge=1.0, le=5.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "workshopId": "987e6543-e21b-12d3-a456-426614174999",
                "workshopName": "Taller Mecánico El Rayo",
                "matchScore": 0.92,
                "reasons": [
                    "Especialista en frenos con 15 años de experiencia",
                    "Excelente calificación (4.8/5)",
                    "A solo 2.3 km de tu ubicación"
                ],
                "distanceKm": 2.3,
                "rating": 4.8
            }
        }





class AnalyzeSentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto a analizar")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto opcional (reviewId, workshopId)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "El servicio fue excelente, muy profesionales y rápidos",
                "context": {
                    "reviewId": "123e4567-e89b-12d3-a456-426614174000",
                    "workshopId": "987e6543-e21b-12d3-a456-426614174999"
                }
            }
        }


class SentimentScores(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0)
    neutral: float = Field(..., ge=0.0, le=1.0)
    negative: float = Field(..., ge=0.0, le=1.0)


class SentimentResult(BaseModel):
    label: SentimentLabelEnum
    score: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza")
    scores: SentimentScores


class SentimentAnalysisResponse(BaseModel):
    id: str
    text: str
    sentiment: SentimentResult
    context: Optional[Dict[str, Any]] = None
    analyzedAt: datetime
    
    class Config:
        from_attributes = True


class BatchSentimentRequest(BaseModel):
    texts: List[Dict[str, str]] = Field(..., max_items=100, description="Lista de textos con ID")
    
    @validator('texts')
    def validate_texts(cls, v):
        for item in v:
            if 'id' not in item or 'text' not in item:
                raise ValueError("Cada item debe tener los campos 'id' y 'text'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    {"id": "review-001", "text": "Excelente atención"},
                    {"id": "review-002", "text": "Tardaron mucho"}
                ]
            }
        }




class AnalyticsDashboardResponse(BaseModel):
    period: Dict[str, str]
    totals: Dict[str, int]
    trends: Dict[str, Any]
    topProblems: List[Dict[str, Any]]


class ProblemsAnalyticsResponse(BaseModel):
    period: str
    totalProblems: int
    categoryDistribution: List[Dict[str, Any]]
    urgencyDistribution: Dict[str, int]


class WorkshopPerformanceResponse(BaseModel):
    workshopId: str
    workshopName: str
    metrics: Dict[str, Any]


class MLModelsMetricsResponse(BaseModel):
    problemClassifier: Dict[str, float]
    workshopRecommender: Dict[str, float]
    sentimentAnalyzer: Dict[str, Any]


class GenerateReportRequest(BaseModel):
    reportType: str = Field(..., description="MONTHLY_SUMMARY, QUARTERLY_SUMMARY, CUSTOM")
    fromDate: str = Field(..., description="Fecha inicio (YYYY-MM-DD)")
    toDate: str = Field(..., description="Fecha fin (YYYY-MM-DD)")
    metrics: List[str] = Field(..., description="Métricas a incluir")
    format: str = Field(default="PDF", description="PDF, EXCEL, JSON")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reportType": "MONTHLY_SUMMARY",
                "fromDate": "2024-10-01",
                "toDate": "2024-10-31",
                "metrics": ["TOTAL_DIAGNOSES", "ACCURACY_RATE", "TOP_PROBLEMS"],
                "format": "PDF"
            }
        }


class ReportResponse(BaseModel):
    id: str
    reportType: str
    period: Dict[str, str]
    format: str
    fileUrl: str = Field(..., description="URL para descargar el reporte")
    generatedAt: datetime



class ErrorResponse(BaseModel):
    error: str
    message: str
    statusCode: int
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "NOT_FOUND",
                "message": "Session not found",
                "statusCode": 404
            }
        }