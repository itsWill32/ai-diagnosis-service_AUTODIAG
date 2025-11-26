
from uuid import UUID
from datetime import datetime
from typing import Protocol

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.entities.diagnosis_message import DiagnosisMessage
from app.domain.value_objects import (
    SessionId,
    UserId,
    VehicleId,
    MessageContent
)
from app.application.dtos.request import StartSessionDto
from app.application.dtos.response import DiagnosisSessionDto


class DiagnosisSessionRepository(Protocol):
    """Interfaz del repositorio de sesiones."""
    
    async def save(self, session: DiagnosisSession) -> DiagnosisSession:
        """Guarda una sesión de diagnóstico."""
        ...
    
    async def find_by_id(self, session_id: SessionId) -> DiagnosisSession | None:
        """Busca una sesión por ID."""
        ...


class VehicleServiceClient(Protocol):
    """Cliente para comunicarse con Vehicle Service."""
    
    async def vehicle_exists(self, vehicle_id: UUID, user_id: UUID) -> bool:
        """Verifica que el vehículo existe y pertenece al usuario."""
        ...


class GeminiChatService(Protocol):
    
    async def send_initial_message(
        self, 
        message: str,
        context: dict
    ) -> str:
        ...


class StartDiagnosisSessionUseCase:

    
    def __init__(
        self,
        session_repository: DiagnosisSessionRepository,
        vehicle_service_client: VehicleServiceClient,
        gemini_service: GeminiChatService
    ):
        self.session_repository = session_repository
        self.vehicle_service_client = vehicle_service_client
        self.gemini_service = gemini_service
    
    async def execute(
        self,
        dto: StartSessionDto,
        user_id: UUID
    ) -> DiagnosisSessionDto:

        vehicle_exists = await self.vehicle_service_client.vehicle_exists(
            vehicle_id=dto.vehicle_id,
            user_id=user_id
        )
        
        if not vehicle_exists:
            raise VehicleNotFoundException(
                f"Vehiculo {dto.vehicle_id} no encontrado o no pertenece al usuario {user_id}"
            )
        
        session = DiagnosisSession.create(
            user_id=UserId.from_string(str(user_id)),
            vehicle_id=VehicleId.from_string(str(dto.vehicle_id))
        )
        
        user_message = DiagnosisMessage.create_user_message(
            session_id=session.get_id(),
            content=MessageContent.create(dto.initial_message)
        )
        
        session.add_message(user_message)
        
        ai_response = await self.gemini_service.send_initial_message(
            message=dto.initial_message,
            context={
                'user_id': str(user_id),
                'vehicle_id': str(dto.vehicle_id),
                'session_id': str(session.get_id().to_string())
            }
        )
        
        assistant_message = DiagnosisMessage.create_assistant_message(
            session_id=session.get_id(),
            content=MessageContent.create(ai_response)
        )
        
        session.add_message(assistant_message)
        
        saved_session = await self.session_repository.save(session)
        
        return self._to_dto(saved_session)
    
    def _to_dto(self, session: DiagnosisSession) -> DiagnosisSessionDto:
        return DiagnosisSessionDto(
            id=UUID(session.get_id().to_string()),
            user_id=UUID(session.get_user_id().to_string()),
            vehicle_id=UUID(session.get_vehicle_id().to_string()),
            status=session.get_status().value,
            started_at=session.get_started_at(),
            completed_at=session.get_completed_at(),
            messages_count=session.get_messages_count(),
            summary=session.get_summary()
        )


class VehicleNotFoundException(Exception):
    """El vehículo no existe."""
    pass


class VehicleNotOwnedByUserException(Exception):
    """El vehículo no pertenece al usuario."""
    pass