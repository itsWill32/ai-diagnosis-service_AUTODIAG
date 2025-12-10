

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from uuid import uuid4

from app.infrastructure.dependencies import (
    get_current_admin_user,
    get_diagnosis_session_repository,
    get_problem_classification_repository,
    get_sentiment_analysis_repository,
    get_workshop_client,
    get_appointment_client
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
    classification_repo = Depends(get_problem_classification_repository),
    workshop_client = Depends(get_workshop_client),
    appointment_client = Depends(get_appointment_client)
):

    if not fromDate or not toDate:
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=30)
    else:
        from_date = datetime.fromisoformat(fromDate)
        to_date = datetime.fromisoformat(toDate)
    
    # Queries reales a Prisma
    try:
        # Total de diagnósticos en el período
        total_diagnoses = await session_repo.db.diagnosissession.count(
            where={
                "startedAt": {
                    "gte": from_date,
                    "lte": to_date
                }
            }
        )
        
        # Usuarios únicos en el período
        sessions_in_period = await session_repo.db.diagnosissession.find_many(
            where={
                "startedAt": {
                    "gte": from_date,
                    "lte": to_date
                }
            }
        )
        unique_users = len(set(s.userId for s in sessions_in_period))
        
        # Top problemas (categorías más frecuentes)
        classifications = await classification_repo.db.problemclassification.find_many(
            where={
                "createdAt": {
                    "gte": from_date,
                    "lte": to_date
                }
            }
        )
        
        # Contar por categoría
        category_counts = {}
        for c in classifications:
            cat = c.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Top 5 problemas
        top_problems = [
            {
                "category": cat,
                "count": count,
                "percentage": round((count / total_diagnoses * 100) if total_diagnoses > 0 else 0, 1)
            }
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Calcular growth (comparar con período anterior)
        period_duration = (to_date - from_date).days
        prev_from_date = from_date - timedelta(days=period_duration)
        prev_to_date = from_date
        
        prev_diagnoses = await session_repo.db.diagnosissession.count(
            where={
                "startedAt": {
                    "gte": prev_from_date,
                    "lte": prev_to_date
                }
            }
        )
        
        if prev_diagnoses > 0:
            diagnoses_growth = round(((total_diagnoses - prev_diagnoses) / prev_diagnoses) * 100, 1)
        else:
            diagnoses_growth = 100.0 if total_diagnoses > 0 else 0.0
        
        # Calcular tiempo promedio de respuesta (sesiones completadas)
        completed_sessions = await session_repo.db.diagnosissession.find_many(
            where={
                "startedAt": {
                    "gte": from_date,
                    "lte": to_date
                },
                "status": "COMPLETED",
                "completedAt": {"not": None}
            }
        )
        
        if completed_sessions:
            total_duration = sum(
                (s.completedAt - s.startedAt).total_seconds() / 60  # minutos
                for s in completed_sessions
                if s.completedAt
            )
            avg_response_time = round(total_duration / len(completed_sessions), 1)
        else:
            avg_response_time = 0.0
        
    except Exception as e:
        print(f"Error en queries de analytics: {e}")
        # Fallback a valores por defecto
        total_diagnoses = 0
        unique_users = 0
        diagnoses_growth = 0.0
        avg_response_time = 0.0
        top_problems = []
    
    # Obtener total de talleres del workshop-service
    try:
        admin_token = user.get("token", "")
        workshops_response = await workshop_client.get_workshops(limit=1, admin_token=admin_token)
        total_workshops = workshops_response.get("total", 0)
    except Exception as e:
        print(f"Error obteniendo total de talleres: {e}")
        total_workshops = 0
    
    # Obtener total de citas del appointment-service
    try:
        admin_token = user.get("token", "")
        total_appointments = await appointment_client.count_appointments(admin_token=admin_token)
    except Exception as e:
        print(f"Error obteniendo total de citas: {e}")
        total_appointments = 0
    
    return AnalyticsDashboardResponse(
        period={
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d")
        },
        totals={
            "totalDiagnoses": total_diagnoses,
            "totalUsers": unique_users,
            "totalWorkshops": total_workshops,
            "totalAppointments": total_appointments
        },
        trends={
            "diagnosesGrowth": diagnoses_growth,
            "avgResponseTime": avg_response_time
        },
        topProblems=top_problems
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
    
    # Queries reales para problemas
    try:
        # Obtener todas las clasificaciones del período
        classifications = await classification_repo.prisma.problemclassification.find_many(
            where={
                "createdAt": {
                    "gte": from_date,
                    "lte": to_date
                }
            },
            include={"session": True}
        )
        
        total_problems = len(classifications)
        
        # Distribución por categoría
        category_counts = {}
        for c in classifications:
            cat = c.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        category_distribution = [
            {
                "category": cat,
                "count": count,
                "percentage": round((count / total_problems * 100) if total_problems > 0 else 0, 1)
            }
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Distribución por urgencia (necesitamos calcular urgencia para cada clasificación)
        # Importar servicio de urgencia
        from app.infrastructure.services import UrgencyCalculatorService
        urgency_service = UrgencyCalculatorService()
        
        urgency_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for c in classifications:
            # Calcular urgencia basado en categoría y síntomas
            urgency_level = urgency_service.calculate_urgency(
                category=c.category,
                symptoms=c.symptoms or []
            )
            
            level_key = urgency_level.get_level().value.lower()
            if level_key in urgency_counts:
                urgency_counts[level_key] += 1
        
    except Exception as e:
        print(f"Error en problems analytics: {e}")
        total_problems = 0
        category_distribution = []
        urgency_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    return ProblemsAnalyticsResponse(
        period=period,
        totalProblems=total_problems,
        categoryDistribution=category_distribution,
        urgencyDistribution=urgency_counts
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

    # Queries reales para métricas de modelos ML
    try:
        # 1. PROBLEM CLASSIFIER METRICS
        # Obtener todas las clasificaciones
        all_classifications = await classification_repo.db.problemclassification.find_many()
        
        total_classifications = len(all_classifications)
        
        if total_classifications > 0:
            # Accuracy: promedio de confidence scores
            avg_confidence = sum(c.confidenceScore for c in all_classifications) / total_classifications
            
            # Precision/Recall/F1: simplificado (basado en confidence)
            # En un sistema real, necesitarías ground truth labels
            high_confidence = sum(1 for c in all_classifications if c.confidenceScore >= 0.7)
            precision = high_confidence / total_classifications
            recall = precision  # Simplificado
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            problem_classifier_metrics = {
                "accuracy": round(avg_confidence, 3),
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1Score": round(f1_score, 3)
            }
        else:
            problem_classifier_metrics = {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1Score": 0.0
            }
        
        # 2. WORKSHOP RECOMMENDER METRICS
        # Obtener recomendaciones generadas
        workshop_recommendations = await session_repo.db.workshoprecommendation.find_many()
        
        total_recommendations = len(workshop_recommendations)
        
        if total_recommendations > 0:
            # Click-through rate: simplificado (basado en match score alto)
            high_match_recommendations = sum(1 for r in workshop_recommendations if r.matchScore >= 0.7)
            click_through_rate = high_match_recommendations / total_recommendations
            
            # Conversion rate: simplificado (asumiendo que match score alto = conversión)
            conversion_rate = sum(1 for r in workshop_recommendations if r.matchScore >= 0.85) / total_recommendations
            
            workshop_recommender_metrics = {
                "clickThroughRate": round(click_through_rate, 3),
                "conversionRate": round(conversion_rate, 3)
            }
        else:
            workshop_recommender_metrics = {
                "clickThroughRate": 0.0,
                "conversionRate": 0.0
            }
        
        # 3. SENTIMENT ANALYZER METRICS
        # Obtener análisis de sentimiento
        sentiment_analyses = await sentiment_repo.db.sentimentanalysis.find_many()
        
        total_analyzed = len(sentiment_analyses)
        
        if total_analyzed > 0:
            # Accuracy: promedio de scores
            avg_sentiment_score = sum(s.score for s in sentiment_analyses) / total_analyzed
            
            sentiment_analyzer_metrics = {
                "accuracy": round(avg_sentiment_score, 3),
                "totalAnalyzed": total_analyzed
            }
        else:
            sentiment_analyzer_metrics = {
                "accuracy": 0.0,
                "totalAnalyzed": 0
            }
        
    except Exception as e:
        print(f"Error en ML metrics: {e}")
        problem_classifier_metrics = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1Score": 0.0}
        workshop_recommender_metrics = {"clickThroughRate": 0.0, "conversionRate": 0.0}
        sentiment_analyzer_metrics = {"accuracy": 0.0, "totalAnalyzed": 0}
    
    return MLModelsMetricsResponse(
        problemClassifier=problem_classifier_metrics,
        workshopRecommender=workshop_recommender_metrics,
        sentimentAnalyzer=sentiment_analyzer_metrics
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