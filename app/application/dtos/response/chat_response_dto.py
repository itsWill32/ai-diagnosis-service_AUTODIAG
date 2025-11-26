
from pydantic import BaseModel, Field
from typing import List
from .diagnosis_message_dto import DiagnosisMessageDto


class ChatResponseDto(BaseModel):

    user_message: DiagnosisMessageDto = Field(
        ...,
        description="Mensaje del usuario"
    )
    
    assistant_message: DiagnosisMessageDto = Field(
        ...,
        description="Respuesta del asistente de IA"
    )
    
    suggested_questions: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Preguntas sugeridas para continuar la conversación",
        example=[
            "¿El ruido ocurre solo al frenar o también en otras situaciones?",
            "¿Hace cuánto tiempo notaste el problema?",
            "¿Has notado algún otro síntoma?"
        ]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_message": {
                    "id": "789e0123-e45b-67c8-d901-234567890abc",
                    "session_id": "456e7890-e12b-34c5-d678-426614174111",
                    "role": "USER",
                    "content": "El ruido suena como un chirrido metálico",
                    "attachments": None,
                    "timestamp": "2024-11-25T10:10:00Z"
                },
                "assistant_message": {
                    "id": "890a1234-b56c-78d9-e012-345678901bcd",
                    "session_id": "456e7890-e12b-34c5-d678-426614174111",
                    "role": "ASSISTANT",
                    "content": "Un chirrido metálico al frenar generalmente indica desgaste en las pastillas de freno...",
                    "attachments": None,
                    "timestamp": "2024-11-25T10:10:05Z"
                },
                "suggested_questions": [
                    "¿El ruido ocurre solo al frenar o también en otras situaciones?",
                    "¿Hace cuánto tiempo notaste el problema?"
                ]
            }
        }