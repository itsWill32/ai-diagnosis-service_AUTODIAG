

from typing import Protocol, Optional
from uuid import UUID
from datetime import datetime

from ..entities import DiagnosisSession, DiagnosisMessage


class DiagnosisSessionRepository(Protocol):

    
    async def save(self, session: DiagnosisSession) -> DiagnosisSession:

        ...
    
    async def find_by_id(self, session_id: UUID) -> Optional[DiagnosisSession]:

        ...
    
    async def find_by_user_id(
        self,
        user_id: UUID,
        vehicle_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> list[DiagnosisSession]:

        ...
    
    async def find_by_vehicle_id(self, vehicle_id: UUID) -> list[DiagnosisSession]:

        ...
    
    async def delete(self, session_id: UUID) -> None:

        ...
    
    
    async def save_message(self, message: DiagnosisMessage) -> DiagnosisMessage:

        ...
    
    async def find_messages_by_session_id(
        self,
        session_id: UUID,
    ) -> list[DiagnosisMessage]:

        ...
    
    async def count_by_user_id(self, user_id: UUID) -> int:

        ...
    
    async def find_active_sessions(
        self,
        user_id: UUID,
    ) -> list[DiagnosisSession]:

        ...