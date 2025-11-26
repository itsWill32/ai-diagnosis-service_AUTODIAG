
from dataclasses import dataclass
from enum import Enum
from typing import List


class ProblemCategoryEnum(str, Enum):

    
    ENGINE = "ENGINE"                      # Motor
    TRANSMISSION = "TRANSMISSION"          # Transmisión
    BRAKES = "BRAKES"                      # Frenos
    ELECTRICAL = "ELECTRICAL"              # Sistema eléctrico
    AIR_CONDITIONING = "AIR_CONDITIONING"  # Aire acondicionado
    SUSPENSION = "SUSPENSION"              # Suspensión
    EXHAUST = "EXHAUST"                    # Sistema de escape
    FUEL_SYSTEM = "FUEL_SYSTEM"            # Sistema de combustible
    COOLING_SYSTEM = "COOLING_SYSTEM"      # Sistema de enfriamiento
    TIRES = "TIRES"                        # Llantas
    BATTERY = "BATTERY"                    # Batería
    LIGHTS = "LIGHTS"                      # Luces
    OTHER = "OTHER"                        # Otros
    
    @classmethod
    def get_description(cls, category: 'ProblemCategoryEnum') -> str:
        descriptions = {
            cls.ENGINE: "Motor",
            cls.TRANSMISSION: "Transmisión",
            cls.BRAKES: "Frenos",
            cls.ELECTRICAL: "Sistema Eléctrico",
            cls.AIR_CONDITIONING: "Aire Acondicionado",
            cls.SUSPENSION: "Suspensión",
            cls.EXHAUST: "Sistema de Escape",
            cls.FUEL_SYSTEM: "Sistema de Combustible",
            cls.COOLING_SYSTEM: "Sistema de Enfriamiento",
            cls.TIRES: "Llantas",
            cls.BATTERY: "Batería",
            cls.LIGHTS: "Luces",
            cls.OTHER: "Otros"
        }
        return descriptions.get(category, "Desconocido")
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        return [category.value for category in cls]


@dataclass(frozen=True)
class ProblemCategory:

    
    value: ProblemCategoryEnum
    
    def __post_init__(self):
        if not isinstance(self.value, ProblemCategoryEnum):
            raise ValueError(
                f"ProblemCategory debe ser un valor del enum ProblemCategoryEnum, "
                f"recibido: {type(self.value)}"
            )
    
    @classmethod
    def from_string(cls, category_str: str) -> 'ProblemCategory':

        try:
            category_enum = ProblemCategoryEnum[category_str.upper()]
            return cls(value=category_enum)
        except KeyError:
            valid_categories = ", ".join(ProblemCategoryEnum.get_all_categories())
            raise ValueError(
                f"Categoría inválida: '{category_str}'. "
                f"Categorías válidas: {valid_categories}"
            )
    
    def to_string(self) -> str:
        return self.value.value
    
    def get_description(self) -> str:
        return ProblemCategoryEnum.get_description(self.value)
    
    def __str__(self) -> str:
        return f"{self.to_string()} ({self.get_description()})"
    
    def __repr__(self) -> str:
        return f"ProblemCategory('{self.to_string()}')"