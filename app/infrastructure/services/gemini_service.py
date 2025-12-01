import google.generativeai as genai
from typing import List, Dict, Optional
import json

from app.infrastructure.config import settings
from app.domain.entities import DiagnosisSession


class GeminiService:
    
    def __init__(self):
        """Inicializa el cliente de Gemini"""
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema para el mecánico virtual"""
        return """
Eres un mecánico automotriz experto con 20 años de experiencia diagnosticando problemas en vehículos.

TU ROL:
- Ayudar a propietarios de vehículos a diagnosticar problemas de forma preliminar
- Hacer preguntas específicas para entender mejor el problema
- Dar diagnósticos claros y comprensibles (sin jerga técnica excesiva)
- Ser empático y tranquilizador (muchos usuarios están preocupados)

REGLAS IMPORTANTES:
1. Siempre pregunta por detalles específicos:
   - ¿Cuándo ocurre el problema? (arranque, en marcha, al frenar, etc.)
   - ¿Hace algún ruido? (chirrido, golpeteo, zumbido, etc.)
   - ¿Hay luces de alerta encendidas en el tablero?
   - ¿Cuánto kilometraje tiene el vehículo?

2. Si el problema es urgente (frenos, dirección, humo, temperatura alta):
   - Marca como CRÍTICO
   - Recomienda NO conducir
   - Sugiere remolque si es necesario

3. Para cada diagnóstico, estructura tu respuesta así:
   - Explicación del problema en lenguaje simple
   - Posibles causas (de más probable a menos probable)
   - Nivel de urgencia (crítico, alto, medio, bajo)
   - Siguiente paso recomendado

4. NO des presupuestos exactos (solo rangos generales)
5. SIEMPRE aclara que es un diagnóstico preliminar y que un mecánico debe verificar

EJEMPLOS DE BUENAS PREGUNTAS:
- "¿El ruido es constante o solo cuando aceleras?"
- "¿La vibración es en el volante o en el asiento?"
- "¿Cuándo fue el último cambio de aceite?"
- "¿El humo es blanco, azul o negro?"

TONO: Profesional, amigable y tranquilizador.
"""
    
    async def generate_response(
        self,
        session: DiagnosisSession,
        user_message: str
    ) -> Dict[str, any]:
        """Genera respuesta del asistente usando Gemini"""
        conversation_history = self._build_conversation_history(session)
        
        conversation_history.append({
            "role": "user",
            "parts": [user_message]
        })
        
        chat = self.model.start_chat(
            history=[
                {"role": "user", "parts": [self.system_prompt]},
                {"role": "model", "parts": ["Entendido. Estoy listo para ayudar con diagnósticos automotrices. ¿Cuál es el problema con tu vehículo?"]}
            ] + conversation_history[:-1]  
        )
        
        response = chat.send_message(user_message)
        assistant_response = response.text
        
        suggested_questions = await self._generate_suggested_questions(
            session,
            user_message,
            assistant_response
        )
        
        symptoms = self._extract_symptoms(session.get_conversation_text())
        
        return {
            "response": assistant_response,
            "suggested_questions": suggested_questions,
            "symptoms_detected": symptoms
        }
    
    async def _generate_suggested_questions(
        self,
        session: DiagnosisSession,
        last_user_message: str,
        last_assistant_response: str
    ) -> List[str]:
        """Genera preguntas de seguimiento usando Gemini"""
        prompt = f"""
Basado en esta conversación sobre un problema automotriz:

Usuario: {last_user_message}
Asistente: {last_assistant_response}

Genera EXACTAMENTE 3 preguntas de seguimiento cortas (máximo 10 palabras cada una) que ayuden a diagnosticar mejor el problema.

Responde ÚNICAMENTE con un JSON array de 3 strings. Ejemplo:
["¿El ruido es constante?", "¿Cuándo fue el último servicio?", "¿Hay luces de alerta?"]
"""
        
        try:
            response = self.model.generate_content(prompt)
            questions_json = response.text.strip()
            
            questions_json = questions_json.replace("```json", "").replace("```", "").strip()
            
            questions = json.loads(questions_json)
            
            if isinstance(questions, list) and len(questions) == 3:
                return questions
            else:
                return self._get_default_questions()
        
        except Exception as e:
            print(f"Error generando preguntas sugeridas: {e}")
            return self._get_default_questions()
    
    def _extract_symptoms(self, conversation_text: str) -> List[str]:
        """Extrae síntomas del texto de la conversación"""
        symptom_keywords = {
            "Ruido anormal": ["ruido", "chirrido", "golpeteo", "zumbido", "rechinido"],
            "Vibración": ["vibración", "vibra", "tiembla", "sacude"],
            "Fuga de líquidos": ["fuga", "gotea", "mancha", "líquido"],
            "Luz de alerta": ["luz", "alerta", "tablero", "check engine", "testigo"],
            "Humo": ["humo", "humea", "vapor"],
            "Olor anormal": ["olor", "huele", "quemado"],
            "Dificultad al arrancar": ["arranca", "arranque", "enciende", "prende"],
            "Pérdida de potencia": ["potencia", "acelera", "fuerza", "lento"],
            "Sobrecalentamiento": ["temperatura", "calor", "sobrecalienta", "caliente"],
            "Consumo excesivo": ["consume", "gasta", "combustible", "gasolina"],
        }
        
        detected_symptoms = []
        conversation_lower = conversation_text.lower()
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in conversation_lower for keyword in keywords):
                detected_symptoms.append(symptom)
        
        return detected_symptoms
    
    def _build_conversation_history(self, session: DiagnosisSession) -> List[Dict]:
        """Construye historial de conversación para Gemini"""
        history = []
        
        for message in session.messages:
            role = "user" if message.is_user_message() else "model"
            history.append({
                "role": role,
                "parts": [message.content.value] 
            })
        
        return history
    
    def _get_default_questions(self) -> List[str]:
        """Retorna preguntas por defecto si falla la generación"""
        return [
            "¿Cuándo notaste el problema por primera vez?",
            "¿El problema es constante o intermitente?",
            "¿Hay algún ruido o luz de alerta?"
        ]