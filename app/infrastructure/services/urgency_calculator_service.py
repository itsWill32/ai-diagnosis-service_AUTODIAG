from typing import List, Tuple
from app.domain.entities import ProblemClassification
from app.domain.value_objects.urgency_level import UrgencyLevelEnum
from app.domain.value_objects.problem_category import ProblemCategoryEnum


class UrgencyCalculatorService:
    
    def __init__(self):
        self.critical_categories = [
            ProblemCategoryEnum.BRAKES,         
            ProblemCategoryEnum.SUSPENSION, 
        ]
        
        self.high_urgency_categories = [
            ProblemCategoryEnum.ENGINE,         
            ProblemCategoryEnum.TRANSMISSION,   
            ProblemCategoryEnum.COOLING_SYSTEM, 
            ProblemCategoryEnum.FUEL_SYSTEM,    
        ]
        
        self.medium_urgency_categories = [
            ProblemCategoryEnum.EXHAUST,
            ProblemCategoryEnum.ELECTRICAL,
            ProblemCategoryEnum.AIR_CONDITIONING,
            ProblemCategoryEnum.BATTERY,
        ]
        
        self.low_urgency_categories = [
            ProblemCategoryEnum.LIGHTS,
            ProblemCategoryEnum.TIRES,
            ProblemCategoryEnum.OTHER,
        ]
        
        self.critical_symptoms = [
            "freno", "frenos", "pedal", "no frena", "se hunde",
            "vibra al frenar", "chirrido al frenar", "humo", "fuego",
            "sobrecalienta", "temperatura alta", "pierde dirección",
            "volante duro", "no gira", "rueda bloqueada",
        ]
        
        self.high_urgency_symptoms = [
            "fuga", "gotea", "mancha", "olor a quemado", "humea",
            "vibración fuerte", "ruido metálico", "no arranca",
            "se apaga", "pierde potencia",
        ]
    
    def calculate_urgency(
        self,
        classification: ProblemClassification
    ) -> Tuple[UrgencyLevelEnum, str, bool, int]: 
        
        category_enum = classification.category.value 
        
        symptoms = classification.symptoms
        
        if category_enum in self.critical_categories:
            return self._create_critical_urgency()
        
        if self._has_critical_symptoms(symptoms):
            return self._create_critical_urgency()
        
        if category_enum in self.high_urgency_categories:
            if self._has_critical_symptoms_for_category(category_enum, symptoms):
                return self._create_critical_urgency()
            
            if self._has_high_urgency_symptoms(symptoms):
                return self._create_high_urgency()
            
            return self._create_high_urgency_moderate()
        
        if category_enum in self.medium_urgency_categories:
            return self._create_medium_urgency()
        
        return self._create_low_urgency()
    
    def _has_critical_symptoms(self, symptoms: List[str]) -> bool:
        symptoms_text = " ".join(symptoms).lower()
        return any(
            critical_symptom in symptoms_text
            for critical_symptom in self.critical_symptoms
        )
    
    def _has_critical_symptoms_for_category(
        self,
        category: ProblemCategoryEnum, 
        symptoms: List[str]
    ) -> bool:
        symptoms_text = " ".join(symptoms).lower()
        
        if category == ProblemCategoryEnum.ENGINE:
            if any(s in symptoms_text for s in ["sobrecalienta", "temperatura alta", "humo"]):
                return True
        
        if category == ProblemCategoryEnum.TRANSMISSION:
            if any(s in symptoms_text for s in ["no entra", "patina", "se atora"]):
                return True
        
        if category == ProblemCategoryEnum.FUEL_SYSTEM:
            if any(s in symptoms_text for s in ["fuga", "gotea", "olor a gasolina"]):
                return True
        
        if category == ProblemCategoryEnum.COOLING_SYSTEM:
            if any(s in symptoms_text for s in ["temperatura alta", "sobrecalienta"]):
                return True
        
        return False
    
    def _has_high_urgency_symptoms(self, symptoms: List[str]) -> bool:
        symptoms_text = " ".join(symptoms).lower()
        return any(
            symptom in symptoms_text
            for symptom in self.high_urgency_symptoms
        )
    
    def _create_critical_urgency(self) -> Tuple[UrgencyLevelEnum, str, bool, int]:
        return (
            UrgencyLevelEnum.CRITICAL,
            "URGENTE: Problema crítico de seguridad. NO conduzca el vehículo. Contacte un servicio de grúa inmediatamente.",
            False,  
            0       
        )
    
    def _create_high_urgency(self) -> Tuple[UrgencyLevelEnum, str, bool, int]:
        return (
            UrgencyLevelEnum.HIGH,
            "ATENCIÓN URGENTE: Problema serio. Evite conducir distancias largas. Taller 24-48h.",
            True,   
            50      
        )
    
    def _create_high_urgency_moderate(self) -> Tuple[UrgencyLevelEnum, str, bool, int]:
        return (
            UrgencyLevelEnum.HIGH,
            "ALTA PRIORIDAD: Requiere atención pronto. Conduzca con precaución. Taller 1-3 días.",
            True,   
            200     
        )
    
    def _create_medium_urgency(self) -> Tuple[UrgencyLevelEnum, str, bool, int]:
        return (
            UrgencyLevelEnum.MEDIUM,
            "PROGRAMAR SERVICIO: Atender en 1-2 semanas.",
            True,   
            1000    
        )
    
    def _create_low_urgency(self) -> Tuple[UrgencyLevelEnum, str, bool, int]:
        return (
            UrgencyLevelEnum.LOW,
            "MANTENIMIENTO PREVENTIVO: Puede esperar al próximo servicio.",
            True,   
            5000    
        )