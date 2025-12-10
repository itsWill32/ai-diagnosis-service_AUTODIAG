

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.infrastructure.dependencies import (
    get_current_user,
    get_current_vehicle_owner,
    get_diagnosis_session_repository,
    get_problem_classification_repository,
    get_workshop_recommender_service,
    get_vehicle_client,
    get_workshop_client
)
from app.infrastructure.api.routers.schemas import (
    WorkshopRecommendationResponse,
    ErrorResponse
)

from app.infrastructure.repositories import PrismaDiagnosisSessionRepository
from app.infrastructure.services import WorkshopRecommenderService
from app.infrastructure.clients import VehicleServiceClient, WorkshopServiceClient


router = APIRouter()


@router.get(
    "/{sessionId}/recommendations",
    response_model=List[WorkshopRecommendationResponse],
    summary="Obtener recomendaciones de talleres",
    description="Recomienda talleres basado en el problema clasificado y ubicación del vehículo",
    responses={
        200: {"description": "Lista de talleres recomendados"},
        404: {"model": ErrorResponse, "description": "Sesión no encontrada o sin clasificación"},
        403: {"model": ErrorResponse, "description": "No autorizado"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_workshop_recommendations(
    sessionId: str,
    limit: int = Query(3, ge=1, le=10, description="Número de recomendaciones"),
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    session_repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository),
    classification_repo = Depends(get_problem_classification_repository),
    recommender_service: WorkshopRecommenderService = Depends(get_workshop_recommender_service),
    vehicle_client: VehicleServiceClient = Depends(get_vehicle_client),
    workshop_client: WorkshopServiceClient = Depends(get_workshop_client)
):
    """
    Obtiene recomendaciones de talleres para una sesión de diagnóstico.
    
    Proceso:
    1. Valida que la sesión pertenezca al usuario
    2. Verifica que exista una clasificación del problema
    3. Obtiene la ubicación del vehículo
    4. Ejecuta el algoritmo ML de recomendación
    5. Enriquece las recomendaciones con datos del taller
    """
    
    # 1. Validar que la sesión existe y pertenece al usuario
    try:
        session = await session_repo.find_by_id(sessionId)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión no encontrada: {sessionId}"
        )
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión no encontrada: {sessionId}"
        )
    
    # Validar ownership
    if session.get_user_id() != user["userId"]:
        raise HTTPException(
            status_code=403,
            detail="No tiene permiso para acceder a esta sesión"
        )
    
    # 2. Verificar que existe clasificación
    try:
        classification = await classification_repo.find_by_session_id(sessionId)
    except Exception:
        classification = None
    
    if not classification:
        raise HTTPException(
            status_code=404,
            detail="No se encontró clasificación para esta sesión. Por favor clasifique el problema primero."
        )
    
    # 3. Obtener ubicación del vehículo
    vehicle_id = session.get_vehicle_id()
    
    try:
        vehicle_data = await vehicle_client.get_vehicle(vehicle_id, f"Bearer {user.get('token', '')}")
    except Exception as e:
        # Si falla, usar ubicación por defecto (Ciudad de México)
        print(f"Error obteniendo vehículo: {e}")
        vehicle_data = None
    
    # Extraer ubicación
    if vehicle_data and vehicle_data.get("latitude") and vehicle_data.get("longitude"):
        user_location = {
            "latitude": vehicle_data["latitude"],
            "longitude": vehicle_data["longitude"]
        }
    else:
        # Ubicación por defecto: Ciudad de México (centro)
        user_location = {
            "latitude": 19.4326,
            "longitude": -99.1332
        }
    
    # 4. Ejecutar algoritmo de recomendación
    category = classification.get_category().value
    
    try:
        recommendations = await recommender_service.recommend_workshops(
            category=category,
            user_location=user_location,
            limit=limit
        )
    except Exception as e:
        print(f"Error en recomendación: {e}")
        # Retornar lista vacía si falla el servicio
        recommendations = []
    
    # 5. Enriquecer recomendaciones con datos completos del taller
    enriched_recommendations = []
    
    for rec in recommendations:
        workshop_id = rec["workshop_id"]
        
        # Obtener detalles completos del taller
        try:
            workshop_details = await workshop_client.get_workshop(workshop_id)
        except Exception:
            workshop_details = None
        
        # Construir respuesta
        enriched_recommendations.append(
            WorkshopRecommendationResponse(
                workshopId=UUID(workshop_id),
                workshopName=rec.get("workshop_name", "Taller"),
                matchScore=rec["match_score"],
                reasons=rec["reasons"],
                distanceKm=rec["distance_km"],
                rating=rec.get("rating", 0.0),
                # Datos adicionales del taller (si están disponibles)
                address=workshop_details.get("address") if workshop_details else None,
                phone=workshop_details.get("phone") if workshop_details else None,
                specialties=[
                    s.get("specialtyType") 
                    for s in workshop_details.get("specialties", [])
                ] if workshop_details else []
            )
        )
    
    return enriched_recommendations