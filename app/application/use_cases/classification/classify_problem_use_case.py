
from uuid import UUID
from typing import Protocol

from app.domain.entities.diagnosis_session import DiagnosisSession
from app.domain.entities.problem_classification import ProblemClassification
from app.domain.value_objects import SessionId, ProblemCategory, ConfidenceScore
from app.application.dtos.response import ProblemClassificationDto


class DiagnosisSessionRepository(Protocol):
    
    async def find_by_id(self, session_id: SessionId) -> DiagnosisSession | None:
        ...


class ProblemClassificationRepository(Protocol):
    
    async def save(self, classification: ProblemClassification) -> ProblemClassification:
        ...
    
    async def find_by_session_id(self, session_id: SessionId) -> ProblemClassification | None:
        ...


class ProblemClassifierService(Protocol):
    
    async def classify(
        self,
        conversation_text: str
    ) -> dict:

        ...


class ClassifyProblemUseCase:

    
    def __init__(
        self,
        session_repository: DiagnosisSessionRepository,
        classification_repository: ProblemClassificationRepository,
        classifier_service: ProblemClassifierService
    ):
        self.session_repository = session_repository
        self.classification_repository = classification_repository
        self.classifier_service = classifier_service
    
    async def execute(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> ProblemClassificationDto:

        session_id_vo = SessionId.from_string(str(session_id))
        session = await self.session_repository.find_by_id(session_id_vo)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        if session.get_user_id().to_string() != str(user_id):
            raise SessionNotOwnedByUserException(
                f"Session {session_id} no le pertenece al usuario {user_id}"
            )
        
        if session.get_messages_count() < 2:
            raise InsufficientDataException(
                "La sesión necesita al menos 2 mensajes para clasificación"
            )
        
        conversation_text = self._extract_conversation_text(session)
        
        classification_result = await self.classifier_service.classify(
            conversation_text=conversation_text
        )
        
        classification = ProblemClassification.create(
            session_id=session.get_id(),
            category=ProblemCategory.from_string(classification_result['category']),
            confidence_score=ConfidenceScore.create(classification_result['confidence_score']),
            subcategory=classification_result.get('subcategory'),
            symptoms=classification_result.get('symptoms', [])
        )
        
        saved_classification = await self.classification_repository.save(classification)
        
        return self._to_dto(saved_classification)
    
    def _extract_conversation_text(self, session: DiagnosisSession) -> str:
        messages = session.get_messages()
        
        user_messages = [
            msg.get_content().to_string()
            for msg in messages
            if msg.get_role().value == 'USER'
        ]
        
        return " | ".join(user_messages)
    
    def _to_dto(self, classification: ProblemClassification) -> ProblemClassificationDto:
        return ProblemClassificationDto(
            id=UUID(classification.get_id().to_string()),
            session_id=UUID(classification.get_session_id().to_string()),
            category=classification.get_category().value,
            subcategory=classification.get_subcategory(),
            confidence_score=classification.get_confidence_score().to_float(),
            symptoms=classification.get_symptoms(),
            created_at=classification.get_created_at()
        )


class SessionNotFoundException(Exception):
    """La sesión no existe."""
    pass


class SessionNotOwnedByUserException(Exception):
    """La sesión no pertenece al usuario."""
    pass


class InsufficientDataException(Exception):
    """No hay suficientes datos para clasificar."""
    pass