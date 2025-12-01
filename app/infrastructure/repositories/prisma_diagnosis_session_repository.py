

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from prisma import Prisma
from prisma.models import DiagnosisSession as PrismaSession
from prisma.models import DiagnosisMessage as PrismaMessage

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.entities.diagnosis_message import DiagnosisMessage
from app.domain.value_objects.session_status import SessionStatus
from app.domain.value_objects.message_role import MessageRole
from app.domain.repository.diagnosis_session_repository import DiagnosisSessionRepository


class PrismaDiagnosisSessionRepository(DiagnosisSessionRepository):
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create(self, session: DiagnosisSession) -> DiagnosisSession:

        prisma_session = await self.db.diagnosissession.create(
            data={
                "id": str(session.id),
                "userId": str(session.user_id),
                "vehicleId": str(session.vehicle_id),
                "status": session.status.value,
                "summary": session.summary,
                "startedAt": session.started_at,
                "completedAt": session.completed_at,
            }
        )
        
        for msg in session.messages:
            await self.db.diagnosismessage.create(
                data={
                    "id": str(msg.id),
                    "sessionId": str(session.id),
                    "role": msg.role.value,
                    "content": msg.content.value,
                    "attachments": msg.attachments if msg.attachments else None,
                    "timestamp": msg.timestamp,
                }
            )
        
        return session
    
    async def update(self, session: DiagnosisSession) -> DiagnosisSession:

        await self.db.diagnosissession.update(
            where={"id": str(session.id)},
            data={
                "status": session.status.value,
                "summary": session.summary,
                "completedAt": session.completed_at,
                "updatedAt": datetime.utcnow(),
            }
        )
        
        existing_messages = await self.db.diagnosismessage.find_many(
            where={"sessionId": str(session.id)}
        )
        existing_ids = {msg.id for msg in existing_messages}
        
        for msg in session.messages:
            if str(msg.id) not in existing_ids:
                await self.db.diagnosismessage.create(
                    data={
                        "id": str(msg.id),
                        "sessionId": str(session.id),
                        "role": msg.role.value,
                        "content": msg.content.value,
                        "attachments": msg.attachments if msg.attachments else None,
                        "timestamp": msg.timestamp,
                    }
                )
        
        return session
    
    async def find_by_id(self, session_id: UUID) -> Optional[DiagnosisSession]:
        prisma_session = await self.db.diagnosissession.find_unique(
            where={"id": str(session_id)},
            include={"messages": True}
        )
        
        if not prisma_session:
            return None
        
        return self._to_domain(prisma_session)
    
    async def find_by_user_id(
        self,
        user_id: str,
        vehicle_id: Optional[str] = None,
        limit: int = 10
    ) -> List[DiagnosisSession]:
        where_clause = {"userId": user_id}
        
        if vehicle_id:
            where_clause["vehicleId"] = vehicle_id
        
        prisma_sessions = await self.db.diagnosissession.find_many(
            where=where_clause,
            include={"messages": True},
            order={"startedAt": "desc"},
            take=limit
        )
        
        return [self._to_domain(s) for s in prisma_sessions]
    
    async def delete(self, session_id: UUID) -> None:
        await self.db.diagnosissession.delete(
            where={"id": str(session_id)}
        )
    
    def _to_domain(self, prisma_session: PrismaSession) -> DiagnosisSession:
        messages = []
        for msg in (prisma_session.messages or []):
            messages.append(
                DiagnosisMessage(
                    id=UUID(msg.id),
                    session_id=UUID(msg.sessionId),
                    role=MessageRole(msg.role),
                    content=msg.content.value,
                    attachments=msg.attachments if msg.attachments else [],
                    timestamp=msg.timestamp
                )
            )
        
        return DiagnosisSession(
            id=UUID(prisma_session.id),
            user_id=UUID(prisma_session.userId),
            vehicle_id=UUID(prisma_session.vehicleId),
            status=SessionStatus(prisma_session.status),
            messages=messages,
            summary=prisma_session.summary,
            started_at=prisma_session.startedAt,
            completed_at=prisma_session.completedAt
        )