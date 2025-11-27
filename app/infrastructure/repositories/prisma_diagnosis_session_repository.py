

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from prisma import Prisma
from prisma.models import DiagnosisSession as PrismaDiagnosisSession
from prisma.models import DiagnosisMessage as PrismaDiagnosisMessage

from app.domain.entities import DiagnosisSession, DiagnosisMessage, SessionStatus
from app.domain.repository import DiagnosisSessionRepository
from app.domain.value_objects import SessionId, UserId, VehicleId
from app.domain.exceptions import SessionNotFoundException


class PrismaDiagnosisSessionRepository(DiagnosisSessionRepository):

    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def save(self, session: DiagnosisSession) -> None:

        session_dict = session.to_dict()
        
        status_value = session_dict["status"].value if hasattr(session_dict["status"], "value") else str(session_dict["status"])
        
        existing = await self.db.diagnosissession.find_unique(
            where={"id": str(session.session_id.value)}
        )
        
        if existing:
            await self.db.diagnosissession.update(
                where={"id": str(session.session_id.value)},
                data={
                    "status": status_value,
                    "summary": session_dict.get("summary"),
                    "completedAt": session_dict.get("completed_at"),
                    "updatedAt": datetime.utcnow(),
                }
            )
        else:
            await self.db.diagnosissession.create(
                data={
                    "id": str(session.session_id.value),
                    "userId": str(session.user_id.value),
                    "vehicleId": str(session.vehicle_id.value),
                    "status": status_value,
                    "summary": session_dict.get("summary"),
                    "startedAt": session_dict["started_at"],
                    "completedAt": session_dict.get("completed_at"),
                }
            )
    
    async def find_by_id(self, session_id: SessionId) -> Optional[DiagnosisSession]:

        prisma_session = await self.db.diagnosissession.find_unique(
            where={"id": str(session_id.value)},
            include={"messages": True}
        )
        
        if not prisma_session:
            return None
        
        return self._to_domain_session(prisma_session)
    
    async def find_by_user_id(
        self,
        user_id: UserId,
        vehicle_id: Optional[VehicleId] = None,
        limit: int = 10
    ) -> List[DiagnosisSession]:

        where_clause = {"userId": str(user_id.value)}
        
        if vehicle_id:
            where_clause["vehicleId"] = str(vehicle_id.value)
        
        prisma_sessions = await self.db.diagnosissession.find_many(
            where=where_clause,
            include={"messages": True},
            order={"startedAt": "desc"},
            take=limit
        )
        
        return [self._to_domain_session(s) for s in prisma_sessions]
    
    async def find_by_vehicle_id(self, vehicle_id: VehicleId) -> List[DiagnosisSession]:

        prisma_sessions = await self.db.diagnosissession.find_many(
            where={"vehicleId": str(vehicle_id.value)},
            include={"messages": True},
            order={"startedAt": "desc"}
        )
        
        return [self._to_domain_session(s) for s in prisma_sessions]
    
    async def delete(self, session_id: SessionId) -> None:

        try:
            await self.db.diagnosissession.delete(
                where={"id": str(session_id.value)}
            )
        except Exception:
            raise SessionNotFoundException(session_id.value)
    
    async def save_message(self, message: DiagnosisMessage) -> None:
 
        message_dict = message.to_dict()
        
        role_value = message_dict["role"].value if hasattr(message_dict["role"], "value") else str(message_dict["role"])
        
        await self.db.diagnosismessage.create(
            data={
                "id": str(message.message_id.value),
                "sessionId": str(message.session_id.value),
                "role": role_value,
                "content": message_dict["content"],
                "attachments": message_dict.get("attachments", []),
                "timestamp": message_dict["timestamp"],
            }
        )
    
    async def find_messages_by_session_id(self, session_id: SessionId) -> List[DiagnosisMessage]:

        prisma_messages = await self.db.diagnosismessage.find_many(
            where={"sessionId": str(session_id.value)},
            order={"timestamp": "asc"}
        )
        
        return [DiagnosisMessage.from_primitives(self._message_to_dict(m)) for m in prisma_messages]
    
    async def count_by_user_id(self, user_id: UserId) -> int:

        return await self.db.diagnosissession.count(
            where={"userId": str(user_id.value)}
        )
    
    async def find_active_sessions(self, user_id: UserId) -> List[DiagnosisSession]:

        prisma_sessions = await self.db.diagnosissession.find_many(
            where={
                "userId": str(user_id.value),
                "status": "ACTIVE"
            },
            include={"messages": True},
            order={"startedAt": "desc"}
        )
        
        return [self._to_domain_session(s) for s in prisma_sessions]
    
    
    def _to_domain_session(self, prisma_session: PrismaDiagnosisSession) -> DiagnosisSession:

        session_dict = {
            "session_id": str(prisma_session.id),
            "user_id": str(prisma_session.userId),
            "vehicle_id": str(prisma_session.vehicleId),
            "status": prisma_session.status,
            "messages": [self._message_to_dict(m) for m in (prisma_session.messages or [])],
            "summary": prisma_session.summary,
            "started_at": prisma_session.startedAt.isoformat(),
            "completed_at": prisma_session.completedAt.isoformat() if prisma_session.completedAt else None,
        }
        
        return DiagnosisSession.from_primitives(session_dict)
    
    def _message_to_dict(self, prisma_message: PrismaDiagnosisMessage) -> dict:

        return {
            "message_id": str(prisma_message.id),
            "session_id": str(prisma_message.sessionId),
            "role": prisma_message.role,
            "content": prisma_message.content,
            "attachments": prisma_message.attachments if prisma_message.attachments else [],
            "timestamp": prisma_message.timestamp.isoformat(),
        }