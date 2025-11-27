

from typing import Tuple, Dict
from app.domain.entities import ProblemClassification
from app.domain.value_objects import ProblemCategory, UrgencyLevel, Money


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
                1200, 3000   
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
    ) -> Tuple[Money, Money, Dict[str, Money], str]:

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
        
        breakdown = {
            "labor_min": Money(amount=labor_min_adj, currency="MXN"),
            "labor_max": Money(amount=labor_max_adj, currency="MXN"),
            "parts_min": Money(amount=parts_min_adj, currency="MXN"),
            "parts_max": Money(amount=parts_max_adj, currency="MXN"),
        }
        
        disclaimer = self._generate_disclaimer(category, urgency_level)
        
        return (
            Money(amount=total_min, currency="MXN"),
            Money(amount=total_max, currency="MXN"),
            breakdown,
            disclaimer
        )
    
    def _generate_disclaimer(
        self,
        category: ProblemCategory,
        urgency_level: UrgencyLevel
    ) -> str:

        base_disclaimer = (

        )
        
        if category in [ProblemCategory.ENGINE, ProblemCategory.TRANSMISSION]:
            base_disclaimer += (
                "\n\n NOTA: Problemas de motor o transmisión pueden tener "
                "costos muy variables. Una inspección presencial es fundamental "
                "para un presupuesto preciso."
            )
        
        if urgency_level == UrgencyLevel.CRITICAL:
            base_disclaimer += (
                "\n\n URGENTE: Los servicios de emergencia pueden tener "
                "cargos adicionales por atención inmediata."
            )
        
        return base_disclaimer
    
    def get_cost_range_text(
        self,
        min_cost: Money,
        max_cost: Money
    ) -> str:

        return (
            f"${min_cost.amount:,.0f} - ${max_cost.amount:,.0f} {min_cost.currency}"
        )
    
    def get_breakdown_text(self, breakdown: Dict[str, Money]) -> str:

        labor_min = breakdown["labor_min"]
        labor_max = breakdown["labor_max"]
        parts_min = breakdown["parts_min"]
        parts_max = breakdown["parts_max"]
        
        return (
            f"Mano de obra: ${labor_min.amount:,.0f} - ${labor_max.amount:,.0f} {labor_min.currency}\n"
            f"Refacciones: ${parts_min.amount:,.0f} - ${parts_max.amount:,.0f} {parts_min.currency}"
        )