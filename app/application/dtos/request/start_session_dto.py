
from pydantic import BaseModel, Field, UUID4


class StartSessionDto(BaseModel):

    vehicle_id: UUID4 = Field(
        ...,
        description="ID del vehículo a diagnosticar",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    initial_message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Descripción inicial del problema",
        example="Mi auto hace un ruido extraño al frenar"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": "123e4567-e89b-12d3-a456-426614174000",
                "initial_message": "Mi auto hace un ruido extraño al frenar"
            }
        }