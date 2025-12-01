from typing import Tuple, Dict
from app.domain.entities import ProblemClassification
from app.domain.value_objects.problem_category import ProblemCategoryEnum
from app.domain.value_objects.urgency_level import UrgencyLevelEnum, UrgencyLevel
from app.domain.value_objects import ProblemCategory, CostEstimate, Currency


class CostEstimatorService:
    
    def __init__(self):
        self.cost_ranges = self._build_cost_ranges()
        
        self.urgency_multipliers = {
            UrgencyLevelEnum.CRITICAL: 1.15,  
            UrgencyLevelEnum.HIGH: 1.10,      
            UrgencyLevelEnum.MEDIUM: 1.0,     
            UrgencyLevelEnum.LOW: 0.95,       
        }
    
    def _build_cost_ranges(self) -> Dict[ProblemCategoryEnum, Tuple[float, float, float, float]]:
        return {
            ProblemCategoryEnum.ENGINE: (1500, 5000, 2000, 15000),
            ProblemCategoryEnum.TRANSMISSION: (1200, 4000, 3000, 20000),
            ProblemCategoryEnum.BRAKES: (400, 800, 800, 1500),
            ProblemCategoryEnum.ELECTRICAL: (500, 1500, 300, 3000),
            ProblemCategoryEnum.AIR_CONDITIONING: (600, 1200, 1000, 4000),
            ProblemCategoryEnum.SUSPENSION: (500, 1000, 1200, 3500),
            ProblemCategoryEnum.EXHAUST: (300, 600, 800, 3000),
            ProblemCategoryEnum.FUEL_SYSTEM: (700, 1500, 1000, 5000),
            ProblemCategoryEnum.COOLING_SYSTEM: (500, 1000, 800, 2500),
            ProblemCategoryEnum.TIRES: (150, 300, 1200, 3000),
            ProblemCategoryEnum.BATTERY: (100, 200, 1500, 3500),
            ProblemCategoryEnum.LIGHTS: (150, 300, 200, 1000),
            ProblemCategoryEnum.OTHER: (300, 1000, 500, 3000),
        }
    
    def estimate_cost(
        self,
        classification: ProblemClassification,
        urgency_level: UrgencyLevel 
    ) -> CostEstimate:

        category_enum = classification.category.value
        if category_enum not in self.cost_ranges:
            category_enum = ProblemCategoryEnum.OTHER
        
        labor_min, labor_max, parts_min, parts_max = self.cost_ranges[category_enum]
        
     
        if hasattr(urgency_level, 'level'):
            u_enum = urgency_level.level
        else:
            u_enum = urgency_level

        urgency_multiplier = self.urgency_multipliers.get(u_enum, 1.0)
        
        labor_min_adj = labor_min * urgency_multiplier
        labor_max_adj = labor_max * urgency_multiplier
        parts_min_adj = parts_min * urgency_multiplier
        parts_max_adj = parts_max * urgency_multiplier
        
        total_min = labor_min_adj + parts_min_adj
        total_max = labor_max_adj + parts_max_adj
        total_avg = (total_min + total_max) / 2
        
        return CostEstimate(
            min_cost=total_min,
            max_cost=total_max,
            average_cost=total_avg,
            currency=Currency.MXN
        )
    
    def get_cost_breakdown(
        self,
        classification: ProblemClassification,
        urgency_level: UrgencyLevel
    ) -> Dict[str, Dict[str, float]]:

        category_enum = classification.category.value
        if category_enum not in self.cost_ranges:
            category_enum = ProblemCategoryEnum.OTHER
        
        labor_min, labor_max, parts_min, parts_max = self.cost_ranges[category_enum]
        
        if hasattr(urgency_level, 'level'):
            u_enum = urgency_level.level
        else:
            u_enum = urgency_level

        urgency_multiplier = self.urgency_multipliers.get(u_enum, 1.0)
        
        return {
            "labor": {
                "min": labor_min * urgency_multiplier,
                "max": labor_max * urgency_multiplier
            },
            "parts": {
                "min": parts_min * urgency_multiplier,
                "max": parts_max * urgency_multiplier
            }
        }
    
    def generate_disclaimer(
        self,
        category: ProblemCategory,
        urgency_level: UrgencyLevel
    ) -> str:
        base_disclaimer = (
            "Esta es una estimación aproximada. "
            "El costo final puede variar según el taller y la inspección detallada."
        )
        
        category_enum = category.value

        if category_enum in [ProblemCategoryEnum.ENGINE, ProblemCategoryEnum.TRANSMISSION]:
            base_disclaimer += (
                "\n\nNOTA: Problemas de motor o transmisión pueden tener "
                "costos muy variables. Una inspección presencial es fundamental "
                "para un presupuesto preciso."
            )
        
        if hasattr(urgency_level, 'level'):
            u_enum = urgency_level.level
        else:
            u_enum = urgency_level

        if u_enum == UrgencyLevelEnum.CRITICAL:
            base_disclaimer += (
                "\n\nURGENTE: Los servicios de emergencia pueden tener "
                "cargos adicionales por atención inmediata."
            )
        
        return base_disclaimer