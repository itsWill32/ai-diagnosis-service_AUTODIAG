

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from uuid import uuid4

from app.infrastructure.dependencies import (
    get_current_admin_user,
    get_diagnosis_session_repository,
    get_problem_classification_repository,
    get_sentiment_analysis_repository
)
from app.infrastructure.api.routers.schemas import (
    AnalyticsDashboardResponse,
    ProblemsAnalyticsResponse,
    WorkshopPerformanceResponse,
    MLModelsMetricsResponse,
    GenerateReportRequest,
    ReportResponse,
    ErrorResponse
)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=AnalyticsDashboardResponse,
    summary="Dashboard general de analytics",
    description="Métricas generales del sistema (solo admin)",
    responses={
        200: {"description": "Dashboard generado"},
        403: {"model": ErrorResponse, "description": "Solo administradores"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_analytics_dashboard(
    fromDate: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    toDate: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    user: Dict[str, Any] = Depends(get_current_admin_user),
    session_repo = Depends(get_diagnosis_session_repository),
    classification_repo = Depends(get_problem_classification_repository)
):

    if not fromDate or not toDate:
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=30)
    else:
        from_date = datetime.fromisoformat(fromDate)
        to_date = datetime.fromisoformat(toDate)
    

    
    return AnalyticsDashboardResponse(
        period={
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d")
        },
        totals={
            "totalDiagnoses": 0,  
            "totalUsers": 0, 
            "totalWorkshops": 0,  
            "totalAppointments": 0
        },
        trends={
            "diagnosesGrowth": 0.0, 
            "avgResponseTime": 0.0  
        },
        topProblems=[
        ]
    )


@router.get(
    "/problems",
    response_model=ProblemsAnalyticsResponse,
    summary="Análisis de problemas comunes",
    description="Estadísticas de categorías más frecuentes",
    responses={
        200: {"description": "Análisis de problemas"},
        403: {"model": ErrorResponse, "description": "Solo administradores"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_problems_analytics(
    period: str = Query("month", description="Período: week, month, quarter, year"),
    user: Dict[str, Any] = Depends(get_current_admin_user),
    classification_repo = Depends(get_problem_classification_repository)
):

    to_date = datetime.utcnow()
    
    if period == "week":
        from_date = to_date - timedelta(days=7)
    elif period == "month":
        from_date = to_date - timedelta(days=30)
    elif period == "quarter":
        from_date = to_date - timedelta(days=90)
    else:  
        from_date = to_date - timedelta(days=365)
    
    
    return ProblemsAnalyticsResponse(
        period=period,
        totalProblems=0,  
        categoryDistribution=[
        ],
        urgencyDistribution={
            "critical": 0,  
            "high": 0,
            "medium": 0,
            "low": 0
        }
    )


@router.get(
    "/workshops/performance",
    response_model=List[WorkshopPerformanceResponse],
    summary="Performance de talleres",
    description="Métricas de efectividad y satisfacción de talleres",
    responses={
        200: {"description": "Performance de talleres"},
        403: {"model": ErrorResponse, "description": "Solo administradores"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_workshops_performance(
    workshopId: Optional[str] = Query(None, description="ID del taller específico"),
    sortBy: str = Query("rating", description="Ordenar por: rating, appointments, sentiment"),
    limit: int = Query(20, ge=1, le=100, description="Número de talleres"),
    user: Dict[str, Any] = Depends(get_current_admin_user),
    sentiment_repo = Depends(get_sentiment_analysis_repository)
):
    
    
    return [] 


@router.get(
    "/ml-models",
    response_model=MLModelsMetricsResponse,
    summary="Métricas de modelos ML",
    description="Precisión y efectividad de los modelos de IA",
    responses={
        200: {"description": "Métricas de modelos ML"},
        403: {"model": ErrorResponse, "description": "Solo administradores"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_ml_models_metrics(
    user: Dict[str, Any] = Depends(get_current_admin_user),
    classification_repo = Depends(get_problem_classification_repository),
    sentiment_repo = Depends(get_sentiment_analysis_repository)
):

    
    return MLModelsMetricsResponse(
        problemClassifier={
            "accuracy": 0.0,  
            "precision": 0.0,
            "recall": 0.0,
            "f1Score": 0.0
        },
        workshopRecommender={
            "clickThroughRate": 0.0,  
            "conversionRate": 0.0
        },
        sentimentAnalyzer={
            "accuracy": 0.0,  
            "totalAnalyzed": 0
        }
    )


@router.post(
    "/reports/generate",
    response_model=ReportResponse,
    summary="Generar reporte personalizado",
    description="Crea un reporte con filtros específicos",
    responses={
        200: {"description": "Reporte generado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        403: {"model": ErrorResponse, "description": "Solo administradores"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def generate_custom_report(
    data: GenerateReportRequest,
    user: Dict[str, Any] = Depends(get_current_admin_user)
):
   
    try:
        from_date = datetime.fromisoformat(data.fromDate)
        to_date = datetime.fromisoformat(data.toDate)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )
    
    if from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="fromDate debe ser anterior a toDate"
        )
    

    
    report_id = str(uuid4())
    
    return ReportResponse(
        id=report_id,
        reportType=data.reportType,
        period={
            "fromDate": data.fromDate,
            "toDate": data.toDate
        },
        format=data.format,
        fileUrl=f"https://cdn.autodiag.com/reports/{report_id}.{data.format.lower()}",  
        generatedAt=datetime.utcnow()
    )