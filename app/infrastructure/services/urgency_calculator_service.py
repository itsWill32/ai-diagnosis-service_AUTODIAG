

from typing import List, Tuple
from app.domain.entities import ProblemClassification
from app.domain.value_objects import UrgencyLevel, ProblemCategory


class UrgencyCalculatorService:

    
    def __init__(self):

        # CATEGORÍAS CRÍTICAS (peligro inmediato)
        self.critical_categories = [
            ProblemCategory.BRAKES,         
            ProblemCategory.SUSPENSION,     
        ]
        
        # CATEGORÍAS DE ALTA URGENCIA
        self.high_urgency_categories = [
            ProblemCategory.ENGINE,         
            ProblemCategory.TRANSMISSION,   
            ProblemCategory.COOLING_SYSTEM, 
            ProblemCategory.FUEL_SYSTEM,    
        ]
        
        # CATEGORÍAS DE URGENCIA MEDIA
        self.medium_urgency_categories = [
            ProblemCategory.EXHAUST,
            ProblemCategory.ELECTRICAL,
            ProblemCategory.AIR_CONDITIONING,
            ProblemCategory.BATTERY,
        ]
        
        # CATEGORÍAS DE BAJA URGENCIA
        self.low_urgency_categories = [
            ProblemCategory.LIGHTS,
            ProblemCategory.TIRES,
            ProblemCategory.OTHER,
        ]
        
        # SÍNTOMAS QUE ELEVAN LA URGENCIA A CRITICAL
        self.critical_symptoms = [
            "freno",
            "frenos",
            "pedal",
            "no frena",
            "se hunde",
            "vibra al frenar",
            "chirrido al frenar",
            "humo",
            "fuego",
            "sobrecalienta",
            "temperatura alta",
            "pierde dirección",
            "volante duro",
            "no gira",
            "rueda bloqueada",
        ]
        
        # SÍNTOMAS QUE ELEVAN LA URGENCIA A HIGH
        self.high_urgency_symptoms = [
            "fuga",
            "gotea",
            "mancha",
            "olor a quemado",
            "humea",
            "vibración fuerte",
            "ruido metálico",
            "no arranca",
            "se apaga",
            "pierde potencia",
        ]
    
    def calculate_urgency(
        self,
        classification: ProblemClassification
    ) -> Tuple[UrgencyLevel, str, bool, int]:
        category = classification.category
        symptoms = classification.symptoms
        
        if category in self.critical_categories:
            return self._create_critical_urgency()
        
        if self._has_critical_symptoms(symptoms):
            return self._create_critical_urgency()
        
        if category in self.high_urgency_categories:
            if self._has_critical_symptoms_for_category(category, symptoms):
                return self._create_critical_urgency()
            
            if self._has_high_urgency_symptoms(symptoms):
                return self._create_high_urgency()
            
            return self._create_high_urgency_moderate()
        
        if category in self.medium_urgency_categories:
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
        category: ProblemCategory,
        symptoms: List[str]
    ) -> bool:

        symptoms_text = " ".join(symptoms).lower()
        
        if category == ProblemCategory.ENGINE:
            if any(s in symptoms_text for s in ["sobrecalienta", "temperatura alta", "humo"]):
                return True
        
        if category == ProblemCategory.TRANSMISSION:
            if any(s in symptoms_text for s in ["no entra", "patina", "se atora"]):
                return True
        
        if category == ProblemCategory.FUEL_SYSTEM:
            if any(s in symptoms_text for s in ["fuga", "gotea", "olor a gasolina"]):
                return True
        
        if category == ProblemCategory.COOLING_SYSTEM:
            if any(s in symptoms_text for s in ["temperatura alta", "sobrecalienta"]):
                return True
        
        return False
    
    def _has_high_urgency_symptoms(self, symptoms: List[str]) -> bool:

        symptoms_text = " ".join(symptoms).lower()
        
        return any(
            symptom in symptoms_text
            for symptom in self.high_urgency_symptoms
        )
    
    
    def _create_critical_urgency(self) -> Tuple[UrgencyLevel, str, bool, int]:

        return (
            UrgencyLevel.CRITICAL,
            "URGENTE: Problema crítico de seguridad. NO conduzca el vehículo. "
            "Contacte un servicio de grúa inmediatamente. Conducir puede poner "
            "en riesgo su vida y la de otros.",
            False,  
            0       
        )
    
    def _create_high_urgency(self) -> Tuple[UrgencyLevel, str, bool, int]:

        return (
            UrgencyLevel.HIGH,
            "ATENCIÓN URGENTE: Problema que puede empeorar rápidamente o causar "
            "daños costosos. Evite conducir distancias largas. Lleve su vehículo "
            "al taller en las próximas 24-48 horas.",
            True,   
            50      
        )
    
    def _create_high_urgency_moderate(self) -> Tuple[UrgencyLevel, str, bool, int]:

        return (
            UrgencyLevel.HIGH,
            "ALTA PRIORIDAD: Problema que requiere atención pronto. Puede seguir "
            "conduciendo con precaución, pero agende una cita en los próximos 1-3 días "
            "para evitar daños mayores.",
            True,   
            200     
        )
    
    def _create_medium_urgency(self) -> Tuple[UrgencyLevel, str, bool, int]:

        return (
            UrgencyLevel.MEDIUM,
            "PROGRAMAR SERVICIO: Problema que debe atenderse en las próximas "
            "1-2 semanas. Es seguro seguir conduciendo, pero no posponga "
            "indefinidamente para evitar que empeore.",
            True,   
            1000    
        )
    
    def _create_low_urgency(self) -> Tuple[UrgencyLevel, str, bool, int]:

        return (
            UrgencyLevel.LOW,
            "MANTENIMIENTO PREVENTIVO: Problema menor que puede atenderse cuando "
            "sea conveniente. Es completamente seguro seguir conduciendo. Agende "
            "servicio en su próximo mantenimiento programado.",
            True,   
            5000    
        )