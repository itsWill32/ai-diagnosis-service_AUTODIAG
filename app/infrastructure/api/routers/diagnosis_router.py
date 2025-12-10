from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.infrastructure.dependencies import (
    get_current_user,
    get_current_vehicle_owner,
    get_diagnosis_session_repository,
    get_gemini_service,
    get_vehicle_client
)
from app.infrastructure.api.routers.schemas import (
    StartSessionRequest,
    SendMessageRequest,
    SessionResponse,
    SessionDetailResponse,
    MessageResponse,
    ChatResponse,
    ErrorResponse
)

from app.infrastructure.repositories import PrismaDiagnosisSessionRepository
from app.infrastructure.services import GeminiService
from app.infrastructure.clients import VehicleServiceClient


router = APIRouter()


@router.get(
    "",
    response_model=List[SessionResponse],
    summary="Listar sesiones del usuario",
    description="Retorna historial de diagnósticos del usuario autenticado"
)
async def get_user_sessions(
    vehicleId: Optional[str] = Query(None, description="Filtrar por vehículo específico"),
    limit: int = Query(10, ge=1, le=50, description="Número de sesiones a retornar"),
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository)
):
    user_id = user["userId"]
    
    sessions = await repo.find_by_user_id(
        user_id=user_id,
        vehicle_id=vehicleId,
        limit=limit
    )
    
    return [
        SessionResponse(
            id=str(s.id),
            userId=str(s.user_id),
            vehicleId=str(s.vehicle_id),
            status=s.status.value,
            startedAt=s.started_at,
            completedAt=s.completed_at,
            messagesCount=len(s.messages),
            summary=s.summary
        )
        for s in sessions
    ]


@router.post(
    "",
    response_model=ChatResponse,
    status_code=201,
    summary="Iniciar nueva sesión de diagnóstico"
)
async def create_diagnosis_session(
    data: StartSessionRequest,
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository),
    gemini: GeminiService = Depends(get_gemini_service),
    vehicle_client: VehicleServiceClient = Depends(get_vehicle_client)
):
    from app.domain.entities.diagnosis_session import DiagnosisSession
    from app.domain.entities.diagnosis_message import DiagnosisMessage
    from app.domain.value_objects.session_status import SessionStatus
    from app.domain.value_objects.message_role import MessageRole
    from app.domain.value_objects import SessionId
    from uuid import uuid4
    from datetime import datetime
    
    user_id = user["userId"]
    vehicle_id = data.vehicleId
    
    auth_token = f"Bearer {user.get('token', '')}"
    
    try:
        vehicle = await vehicle_client.get_vehicle(
            vehicle_id=vehicle_id,
            user_id=user_id,
            auth_token=auth_token
        )
    except Exception as e:
        pass
    
    session = DiagnosisSession(
        session_id=SessionId(uuid4()),
        user_id=UUID(user_id),
        vehicle_id=UUID(vehicle_id),
        status=SessionStatus.ACTIVE,
        messages=[],
        started_at=datetime.utcnow()
    )
    
    user_message = DiagnosisMessage.create(
        session_id=session.id.value,
        role=MessageRole.USER,
        content=data.initialMessage
    )
    
    session.add_message(user_message)
    
    try:
        gemini_response = await gemini.generate_response(
            session=session,
            user_message=data.initialMessage
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
    
    assistant_message = DiagnosisMessage.create(
        session_id=session.id.value,
        role=MessageRole.ASSISTANT,
        content=gemini_response["response"]
    )
    
    session.add_message(assistant_message)
    
    await repo.create(session)
    
    return ChatResponse(
        userMessage=MessageResponse(
            id=str(user_message.id.value),
            sessionId=str(session.id.value),
            role="USER",
            content=user_message.content.value,
            timestamp=user_message.timestamp
        ),
        assistantMessage=MessageResponse(
            id=str(assistant_message.id.value),
            sessionId=str(session.id.value),
            role="ASSISTANT",
            content=assistant_message.content.value,
            timestamp=assistant_message.timestamp
        ),
        suggestedQuestions=gemini_response.get("suggested_questions", [])
    )


@router.get(
    "/{sessionId}",
    response_model=SessionDetailResponse,
    summary="Obtener sesión de diagnóstico"
)
async def get_session_by_id(
    sessionId: str,
    user: Dict[str, Any] = Depends(get_current_user),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository)
):
    from app.infrastructure.dependencies import (
        get_problem_classification_repository,
        get_urgency_calculator_service,
        get_cost_estimator_service,
        get_workshop_recommender_service,
        get_vehicle_client,
        get_workshop_client
    )
    from app.infrastructure.api.routers.schemas import (
        ClassificationResponse,
        UrgencyResponse,
        CostEstimateResponse,
        CostBreakdown,
        WorkshopRecommendationResponse
    )

    user_id = user["userId"]

    session = await repo.find_by_id(UUID(sessionId))

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión {sessionId} no encontrada"
        )

    if str(session.user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a esta sesión"
        )

    # Inicializar valores por defecto
    classification_data = None
    urgency_data = None
    cost_estimate_data = None
    recommendations_data = []

    # Obtener clasificación si existe
    classification_repo = get_problem_classification_repository()

    try:
        classification = await classification_repo.find_by_session_id(sessionId)

        if classification:
            # Construir response de clasificación
            classification_data = {
                "id": str(classification.id),
                "sessionId": sessionId,
                "category": classification.category.value,
                "subcategory": classification.subcategory,
                "confidenceScore": classification.confidence_score.value,
                "symptoms": classification.symptoms,
                "createdAt": classification.created_at.isoformat() if hasattr(classification.created_at, 'isoformat') else str(classification.created_at)
            }

            # Calcular urgencia
            urgency_calc = get_urgency_calculator_service()
            urgency_level, description, safe_to_drive, max_km = urgency_calc.calculate_urgency(classification)

            urgency_data = {
                "level": urgency_level.value,
                "description": description,
                "safeToDriver": safe_to_drive,
                "maxMileageRecommended": max_km
            }

            # Calcular estimación de costos
            cost_estimator = get_cost_estimator_service()
            min_cost, max_cost, breakdown, disclaimer = cost_estimator.estimate_cost(
                classification, urgency_level
            )

            cost_estimate_data = {
                "minCost": min_cost,
                "maxCost": max_cost,
                "currency": "MXN",
                "breakdown": {
                    "partsMin": breakdown["parts"]["min"],
                    "partsMax": breakdown["parts"]["max"],
                    "laborMin": breakdown["labor"]["min"],
                    "laborMax": breakdown["labor"]["max"]
                },
                "disclaimer": disclaimer
            }

            # Obtener recomendaciones de talleres
            try:
                vehicle_client = get_vehicle_client()

                # Obtener ubicación del vehículo
                vehicle_id = str(session.vehicle_id)
                auth_token = f"Bearer {user.get('token', '')}"

                try:
                    vehicle_data = await vehicle_client.get_vehicle(vehicle_id, user_id, auth_token)

                    if vehicle_data and vehicle_data.get("latitude") and vehicle_data.get("longitude"):
                        user_location = {
                            "latitude": vehicle_data["latitude"],
                            "longitude": vehicle_data["longitude"]
                        }
                    else:
                        # Ubicación por defecto: Ciudad de México
                        user_location = {
                            "latitude": 19.4326,
                            "longitude": -99.1332
                        }
                except Exception:
                    user_location = {
                        "latitude": 19.4326,
                        "longitude": -99.1332
                    }

                # Obtener recomendaciones
                recommender_service = get_workshop_recommender_service()
                category = classification.category.value

                recommendations = await recommender_service.recommend_workshops(
                    category=category,
                    user_location=user_location,
                    limit=3
                )

                # Enriquecer con datos del workshop-service
                workshop_client = get_workshop_client()

                for rec in recommendations:
                    workshop_id = rec["workshop_id"]

                    try:
                        workshop_details = await workshop_client.get_workshop(workshop_id)
                    except Exception:
                        workshop_details = None

                    recommendations_data.append({
                        "workshopId": workshop_id,
                        "workshopName": rec.get("workshop_name", "Taller"),
                        "matchScore": rec["match_score"],
                        "reasons": rec["reasons"],
                        "distanceKm": rec["distance_km"],
                        "rating": rec.get("rating", 0.0),
                        "address": workshop_details.get("address") if workshop_details else None,
                        "phone": workshop_details.get("phone") if workshop_details else None,
                        "specialties": [
                            s.get("specialtyType")
                            for s in workshop_details.get("specialties", [])
                        ] if workshop_details else []
                    })

            except Exception as e:
                print(f"Error obteniendo recomendaciones: {e}")
                recommendations_data = []

    except Exception as e:
        print(f"Error obteniendo clasificación: {e}")

    return SessionDetailResponse(
        id=str(session.id.value),
        userId=str(session.user_id),
        vehicleId=str(session.vehicle_id),
        status=session.status.value,
        startedAt=session.started_at,
        completedAt=session.completed_at,
        messagesCount=len(session.messages),
        summary=session.summary,
        classification=classification_data,
        urgency=urgency_data,
        costEstimate=cost_estimate_data,
        recommendations=recommendations_data
    )


@router.get(
    "/{sessionId}/messages",
    response_model=List[MessageResponse],
    summary="Obtener mensajes de la sesión"
)
async def get_session_messages(
    sessionId: str,
    user: Dict[str, Any] = Depends(get_current_user),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository)
):
    user_id = user["userId"]
    
    session = await repo.find_by_id(UUID(sessionId))
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión {sessionId} no encontrada"
        )
    
    if str(session.user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a esta sesión"
        )
    
    return [
        MessageResponse(
            id=str(msg.id.value),
            sessionId=str(session.id.value),
            role=msg.role.value,
            content=msg.content.value,
            timestamp=msg.timestamp
        )
        for msg in session.messages
    ]


@router.post(
    "/{sessionId}/messages",
    response_model=ChatResponse,
    summary="Enviar mensaje al chatbot"
)
async def send_message(
    sessionId: str,
    data: SendMessageRequest,
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository),
    gemini: GeminiService = Depends(get_gemini_service)
):
    from app.domain.entities.diagnosis_message import DiagnosisMessage
    from app.domain.value_objects.message_role import MessageRole
    from app.domain.value_objects.session_status import SessionStatus
    from uuid import uuid4
    from datetime import datetime
    
    user_id = user["userId"]
    
    session = await repo.find_by_id(UUID(sessionId))
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Sesión {sessionId} no encontrada"
        )
    
    if str(session.user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a esta sesión"
        )
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"La sesión está {session.status.value}, no se pueden enviar mensajes"
        )
    
    user_message = DiagnosisMessage.create(
        session_id=session.id.value,
        role=MessageRole.USER,
        content=data.content
    )
    
    session.add_message(user_message)
    
    try:
        gemini_response = await gemini.generate_response(
            session=session,
            user_message=data.content
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
    
    assistant_message = DiagnosisMessage.create(
        session_id=session.id.value,
        role=MessageRole.ASSISTANT,
        content=gemini_response["response"]
    )
    
    session.add_message(assistant_message)
    
    await repo.update(session)
    
    return ChatResponse(
        userMessage=MessageResponse(
            id=str(user_message.id.value),
            sessionId=str(session.id.value),
            role="USER",
            content=user_message.content.value,
            timestamp=user_message.timestamp
        ),
        assistantMessage=MessageResponse(
            id=str(assistant_message.id.value),
            sessionId=str(session.id.value),
            role="ASSISTANT",
            content=assistant_message.content.value,
            timestamp=assistant_message.timestamp
        ),
        suggestedQuestions=gemini_response.get("suggested_questions", [])
    )