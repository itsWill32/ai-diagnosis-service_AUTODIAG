
from typing import Tuple, Dict
from app.domain.entities import ProblemClassification
from app.domain.value_objects import ProblemCategory, UrgencyLevel, CostEstimate, Currency


class CostEstimatorService:
    
    def __init__(self):
        self.cost_ranges = self._build_cost_ranges()
        
        self.urgency_multipliers = {
            UrgencyLevel.CRITICAL: 1.15,  
            UrgencyLevel.HIGH: 1.10,      
            UrgencyLevel.MEDIUM: 1.0,     
            UrgencyLevel.LOW: 0.95,       
        }
    
    def _build_cost_ranges(self) -> Dict[ProblemCategory, Tuple[float, float, float, float]]:
        return {
            ProblemCategory.ENGINE: (
                1500, 5000,   
                2000, 15000   
            ),
            
            ProblemCategory.TRANSMISSION: (
                1200, 4000,
                3000, 20000
            ),
            
            ProblemCategory.BRAKES: (
                400, 800,
                800, 1500
            ),
            
            ProblemCategory.ELECTRICAL: (
                500, 1500,
                300, 3000
            ),
            
            ProblemCategory.AIR_CONDITIONING: (
                600, 1200,
                1000, 4000
            ),
            
            ProblemCategory.SUSPENSION: (
                500, 1000,
                1200, 3500
            ),
            
            ProblemCategory.EXHAUST: (
                300, 600,
                800, 3000
            ),
            
            ProblemCategory.FUEL_SYSTEM: (
                700, 1500,
                1000, 5000
            ),
            
            ProblemCategory.COOLING_SYSTEM: (
                500, 1000,
                800, 2500
            ),
            
            ProblemCategory.TIRES: (
                150, 300,     
                1200, 3000    # Parts (4 tires)
            ),
            
            ProblemCategory.BATTERY: (
                100, 200,
                1500, 3500
            ),
            
            ProblemCategory.LIGHTS: (
                150, 300,
                200, 1000
            ),
            
            ProblemCategory.OTHER: (
                300, 1000,
                500, 3000
            ),
        }
    
    def estimate_cost(
        self,
        classification: ProblemClassification,
        urgency_level: UrgencyLevel
    ) -> CostEstimate:

        category = classification.category
        
        if category not in self.cost_ranges:
            category = ProblemCategory.OTHER
        
        labor_min, labor_max, parts_min, parts_max = self.cost_ranges[category]
        
        urgency_multiplier = self.urgency_multipliers.get(urgency_level, 1.0)
        
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

        category = classification.category
        
        if category not in self.cost_ranges:
            category = ProblemCategory.OTHER
        
        labor_min, labor_max, parts_min, parts_max = self.cost_ranges[category]
        urgency_multiplier = self.urgency_multipliers.get(urgency_level, 1.0)
        
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
        
        if category in [ProblemCategory.ENGINE, ProblemCategory.TRANSMISSION]:
            base_disclaimer += (
                "\n\nNOTA: Problemas de motor o transmisión pueden tener "
                "costos muy variables. Una inspección presencial es fundamental "
                "para un presupuesto preciso."
            )
        
        if urgency_level == UrgencyLevel.CRITICAL:
            base_disclaimer += (
                "\n\nURGENTE: Los servicios de emergencia pueden tener "
                "cargos adicionales por atención inmediata."
            )
        
        return base_disclaimer