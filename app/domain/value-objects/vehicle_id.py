

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class VehicleId:

    
    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError(f"VehicleId debe ser un UUID válido, recibido: {type(self.value)}")
    
    @classmethod
    def from_string(cls, vehicle_id_str: str) -> 'VehicleId':

        try:
            uuid_obj = UUID(vehicle_id_str)
            return cls(value=uuid_obj)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"String inválido para VehicleId: {vehicle_id_str}") from e
    
    def to_string(self) -> str:
        return str(self.value)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"VehicleId('{self.to_string()}')"