

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
    description="Retorna historial de diagnósticos del usuario autenticado",
    responses={
        200: {"description": "Lista de sesiones"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_user_sessions(
    vehicleId: Optional[str] = Query(None, description="Filtrar por vehículo específico"),
    limit: int = Query(10, ge=1, le=50, description="Número de sesiones a retornar"),
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo: PrismaDiagnosisSessionRepository = Depends(get_diagnosis_session_repository)
):

    user_id = user["userId"]
    
    sessions = await repo.find_by_user_id(user_id, limit=limit)
    
    if vehicleId:
        sessions = [s for s in sessions if s.vehicle_id == vehicleId]
    
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
    summary="Iniciar nueva sesión de diagnóstico",
    description="Crea una nueva conversación con el chatbot de IA",
    responses={
        201: {"description": "Sesión creada exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Vehículo no encontrado"}
    }
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
    from uuid import uuid4
    from datetime import datetime
    
    user_id = user["userId"]
    vehicle_id = data.vehicleId
    
    auth_token = f"Bearer {user.get('token', '')}"  # Token JWT
    
    vehicle = await vehicle_client.get_vehicle(
        vehicle_id=vehicle_id,
        user_id=user_id,
        auth_token=auth_token
    )
    
    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail=f"Vehículo {vehicle_id} no encontrado o no pertenece al usuario"
        )
    
    session = DiagnosisSession(
        id=uuid4(),
        user_id=UUID(user_id),
        vehicle_id=UUID(vehicle_id),
        status=SessionStatus.ACTIVE,
        started_at=datetime.utcnow(),
        messages=[]
    )
    
    user_message = DiagnosisMessage(
        id=uuid4(),
        session_id=session.id,
        role=MessageRole.USER,
        content=data.initialMessage,
        timestamp=datetime.utcnow()
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
    
    assistant_message = DiagnosisMessage(
        id=uuid4(),
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=gemini_response["response"],
        timestamp=datetime.utcnow()
    )
    
    session.add_message(assistant_message)
    
    saved_session = await repo.create(session)
    
    return ChatResponse(
        userMessage=MessageResponse(
            id=str(user_message.id),
            sessionId=str(session.id),
            role="USER",
            content=user_message.content,
            timestamp=user_message.timestamp
        ),
        assistantMessage=MessageResponse(
            id=str(assistant_message.id),
            sessionId=str(session.id),
            role="ASSISTANT",
            content=assistant_message.content,
            timestamp=assistant_message.timestamp
        ),
        suggestedQuestions=gemini_response.get("suggested_questions", [])
    )



@router.get(
    "/{sessionId}",
    response_model=SessionDetailResponse,
    summary="Obtener sesión de diagnóstico",
    description="Retorna información completa de una sesión",
    responses={
        200: {"description": "Sesión encontrada"},
        404: {"model": ErrorResponse, "description": "Sesión no encontrada"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_session_by_id(
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
    
  
    return SessionDetailResponse(
        id=str(session.id),
        userId=str(session.user_id),
        vehicleId=str(session.vehicle_id),
        status=session.status.value,
        startedAt=session.started_at,
        completedAt=session.completed_at,
        messagesCount=len(session.messages),
        summary=session.summary,
        classification=None,
        urgency=None,  
        costEstimate=None,  
        recommendations=[]  
    )




@router.get(
    "/{sessionId}/messages",
    response_model=List[MessageResponse],
    summary="Obtener mensajes de la sesión",
    description="Retorna historial completo de la conversación",
    responses={
        200: {"description": "Mensajes de la sesión"},
        404: {"model": ErrorResponse, "description": "Sesión no encontrada"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
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
            id=str(msg.id),
            sessionId=str(session.id),
            role=msg.role.value,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in session.messages
    ]




@router.post(
    "/{sessionId}/messages",
    response_model=ChatResponse,
    summary="Enviar mensaje al chatbot",
    description="Envía un mensaje del usuario y recibe respuesta de la IA",
    responses={
        200: {"description": "Mensaje procesado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        404: {"model": ErrorResponse, "description": "Sesión no encontrada"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
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
    
    user_message = DiagnosisMessage(
        id=uuid4(),
        session_id=session.id,
        role=MessageRole.USER,
        content=data.content,
        timestamp=datetime.utcnow()
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
    
    assistant_message = DiagnosisMessage(
        id=uuid4(),
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=gemini_response["response"],
        timestamp=datetime.utcnow()
    )
    
    session.add_message(assistant_message)
    
    await repo.update(session)
    
    return ChatResponse(
        userMessage=MessageResponse(
            id=str(user_message.id),
            sessionId=str(session.id),
            role="USER",
            content=user_message.content,
            timestamp=user_message.timestamp
        ),
        assistantMessage=MessageResponse(
            id=str(assistant_message.id),
            sessionId=str(session.id),
            role="ASSISTANT",
            content=assistant_message.content,
            timestamp=assistant_message.timestamp
        ),
        suggestedQuestions=gemini_response.get("suggested_questions", [])
    )