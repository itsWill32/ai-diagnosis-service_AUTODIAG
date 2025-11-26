
from dataclasses import dataclass
from enum import Enum


class UrgencyLevelEnum(str, Enum):

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class UrgencyLevel:

    level: UrgencyLevelEnum
    description: str
    safe_to_drive: bool
    max_mileage_recommended: int | None = None
    
    def __post_init__(self):
        if not isinstance(self.level, UrgencyLevelEnum):
            raise ValueError(
                f"level debe ser UrgencyLevelEnum, recibido: {type(self.level)}"
            )
        
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description no puede estar vacía")
        
        if not isinstance(self.safe_to_drive, bool):
            raise ValueError(
                f"safe_to_drive debe ser boolean, recibido: {type(self.safe_to_drive)}"
            )
        
        if self.max_mileage_recommended is not None:
            if not isinstance(self.max_mileage_recommended, int):
                raise ValueError(
                    f"max_mileage_recommended debe ser int, recibido: {type(self.max_mileage_recommended)}"
                )
            if self.max_mileage_recommended < 0:
                raise ValueError(
                    f"max_mileage_recommended no puede ser negativo: {self.max_mileage_recommended}"
                )
    
    @classmethod
    def create_critical(cls, description: str) -> 'UrgencyLevel':

        return cls(
            level=UrgencyLevelEnum.CRITICAL,
            description=description,
            safe_to_drive=False,
            max_mileage_recommended=0
        )
    
    @classmethod
    def create_high(cls, description: str, max_mileage: int | None = None) -> 'UrgencyLevel':

        return cls(
            level=UrgencyLevelEnum.HIGH,
            description=description,
            safe_to_drive=True,
            max_mileage_recommended=max_mileage
        )
    
    @classmethod
    def create_medium(cls, description: str) -> 'UrgencyLevel':

        return cls(
            level=UrgencyLevelEnum.MEDIUM,
            description=description,
            safe_to_drive=True,
            max_mileage_recommended=None
        )
    
    @classmethod
    def create_low(cls, description: str) -> 'UrgencyLevel':

        return cls(
            level=UrgencyLevelEnum.LOW,
            description=description,
            safe_to_drive=True,
            max_mileage_recommended=None
        )
    
    @classmethod
    def from_string(cls, level_str: str, description: str, 
                    safe_to_drive: bool, max_mileage: int | None = None) -> 'UrgencyLevel':

        try:
            level_enum = UrgencyLevelEnum(level_str.upper())
            return cls(
                level=level_enum,
                description=description,
                safe_to_drive=safe_to_drive,
                max_mileage_recommended=max_mileage
            )
        except ValueError as e:
            raise ValueError(
                f"Nivel de urgencia inválido: {level_str}. "
                f"Valores válidos: {[e.value for e in UrgencyLevelEnum]}"
            ) from e
    
    def get_level(self) -> str:
        return self.level.value
    
    def get_description(self) -> str:
        return self.description
    
    def is_safe_to_drive(self) -> bool:
        return self.safe_to_drive
    
    def is_critical(self) -> bool:
        return self.level == UrgencyLevelEnum.CRITICAL
    
    def requires_immediate_attention(self) -> bool:
        return self.level in [UrgencyLevelEnum.CRITICAL, UrgencyLevelEnum.HIGH]
    
    def get_color_code(self) -> str:

        color_map = {
            UrgencyLevelEnum.CRITICAL: "red",
            UrgencyLevelEnum.HIGH: "orange",
            UrgencyLevelEnum.MEDIUM: "yellow",
            UrgencyLevelEnum.LOW: "green"
        }
        return color_map[self.level]
    
    def __str__(self) -> str:
        return self.level.value
    
    def __repr__(self) -> str:
        return (
            f"UrgencyLevel(level={self.level.value}, "
            f"safe_to_drive={self.safe_to_drive}, "
            f"max_mileage={self.max_mileage_recommended})"
        )