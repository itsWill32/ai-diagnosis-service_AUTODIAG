from typing import Dict, List, Tuple, Optional
from uuid import uuid4

from app.domain.entities import DiagnosisSession, ProblemClassification
from app.domain.value_objects import ProblemCategory, ConfidenceScore


class ProblemClassifierService:
    
    def __init__(self):
        self.category_keywords = self._build_keyword_dictionary()
        self.min_confidence_threshold = 0.5
    
    def _build_keyword_dictionary(self) -> Dict[str, Dict[str, float]]:
        return {
            "ENGINE": { "motor": 5.0, "pistón": 5.0, "biela": 5.0, "válvula": 5.0, "cilindro": 5.0, "bujía": 5.0, "aceite": 4.0, "filtro de aceite": 4.0, "correa de distribución": 4.0, "cadena de distribución": 4.0, "humea": 3.0, "humo": 3.0, "temperatura": 3.0, "sobrecalienta": 3.0, "ruido del motor": 2.0, "vibración del motor": 2.0 },
            "TRANSMISSION": { "transmisión": 5.0, "caja": 5.0, "cambios": 5.0, "embrague": 5.0, "clutch": 5.0, "primera velocidad": 4.0, "segunda velocidad": 4.0, "reversa": 4.0, "neutro": 4.0, "patina": 3.0, "no entra": 3.0, "se atora": 3.0 },
            "BRAKES": { "freno": 5.0, "frenos": 5.0, "pastilla": 5.0, "disco de freno": 5.0, "tambor": 5.0, "pedal de freno": 4.0, "líquido de frenos": 4.0, "abs": 4.0, "chirrido al frenar": 3.0, "vibra al frenar": 3.0, "se hunde el pedal": 3.0 },
            "ELECTRICAL": { "eléctrico": 5.0, "batería": 5.0, "alternador": 5.0, "marcha": 5.0, "fusible": 5.0, "no arranca": 4.0, "luz de batería": 4.0, "corto circuito": 4.0, "descarga": 3.0, "voltaje": 3.0 },
            "AIR_CONDITIONING": { "aire acondicionado": 5.0, "clima": 5.0, "a/c": 5.0, "compresor": 5.0, "no enfría": 4.0, "gas refrigerante": 4.0, "condensador": 4.0, "ventilador": 3.0, "temperatura interior": 3.0 },
            "SUSPENSION": { "suspensión": 5.0, "amortiguador": 5.0, "resorte": 5.0, "barra estabilizadora": 5.0, "rótula": 4.0, "brazo": 4.0, "buje": 4.0, "brincos": 3.0, "duro al manejar": 3.0 },
            "EXHAUST": { "escape": 5.0, "mofle": 5.0, "catalizador": 5.0, "tubo de escape": 5.0, "humo negro": 4.0, "humo azul": 4.0, "humo blanco": 4.0, "ruido fuerte": 3.0 },
            "FUEL_SYSTEM": { "combustible": 5.0, "gasolina": 5.0, "diesel": 5.0, "inyector": 5.0, "bomba de gasolina": 5.0, "consume mucho": 4.0, "gasta mucho": 4.0, "olor a gasolina": 4.0, "tanque": 3.0 },
            "COOLING_SYSTEM": { "radiador": 5.0, "anticongelante": 5.0, "refrigerante": 5.0, "termostato": 5.0, "temperatura alta": 4.0, "sobrecalienta": 4.0, "ventilador": 4.0 },
            "TIRES": { "llanta": 5.0, "neumático": 5.0, "rin": 5.0, "ponchadura": 4.0, "presión": 4.0, "desgaste": 4.0 },
            "BATTERY": { "batería": 5.0, "acumulador": 5.0, "se descarga": 4.0, "no prende": 4.0 },
            "LIGHTS": { "faro": 5.0, "luz": 5.0, "lámpara": 5.0, "no enciende": 4.0, "parpadea": 4.0 },
        }
    
    async def classify_problem(
        self,
        session: DiagnosisSession
    ) -> ProblemClassification:
        
        session.validate_can_classify()
        
        conversation_text = session.get_conversation_text().lower()
        
        category_scores = self._calculate_category_scores(conversation_text)
        
        best_category, best_score = self._select_best_category(category_scores)
        
        confidence = self._calculate_confidence(best_score, category_scores)
        
        subcategory = self._extract_subcategory(conversation_text, best_category)
        
        symptoms = self._extract_symptoms_for_category(conversation_text, best_category)
        
        classification = ProblemClassification.create(
            session_id=session.id,     
            category=best_category,    
            subcategory=subcategory,
            confidence=confidence,     
            symptoms=symptoms
        )
        
        return classification
    
    def _calculate_category_scores(self, text: str) -> Dict[str, float]:
        scores = {category: 0.0 for category in self.category_keywords.keys()}
        for category, keywords in self.category_keywords.items():
            for keyword, weight in keywords.items():
                occurrences = text.count(keyword)
                scores[category] += weight * occurrences
        return scores
    
    def _select_best_category(
        self,
        category_scores: Dict[str, float]
    ) -> Tuple[str, float]:
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        if best_score == 0.0:
            return "OTHER", 0.0
        return best_category, best_score
    
    def _calculate_confidence(
        self,
        best_score: float,
        all_scores: Dict[str, float]
    ) -> float:
        if best_score == 0.0:
            return 0.0
        total_score = sum(all_scores.values())
        confidence = best_score / total_score
        confidence = max(0.5, min(1.0, confidence))
        return round(confidence, 2)
    
    def _extract_subcategory(
        self,
        text: str,
        category: str
    ) -> Optional[str]:
        return None
    
    def _extract_symptoms_for_category(
        self,
        text: str,
        category: str
    ) -> List[str]:
        symptoms = []
        if category in self.category_keywords:
            for keyword, weight in self.category_keywords[category].items():
                if keyword in text:
                    symptoms.append(keyword)
        return symptoms[:5]