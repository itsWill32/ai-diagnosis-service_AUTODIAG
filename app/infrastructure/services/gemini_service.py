import google.generativeai as genai
from typing import List, Dict, Optional
import json

from app.infrastructure.config import settings
from app.domain.entities import DiagnosisSession


class GeminiService:

    
    def __init__(self):
 
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:

        return 
    
    async def generate_response(
        self,
        session: DiagnosisSession,
        user_message: str
    ) -> Dict[str, any]:

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

        history = []
        
        for message in session.messages:
            role = "user" if message.is_user_message() else "model"
            history.append({
                "role": role,
                "parts": [message.content.value]  
            })
        
        return history
    
    def _get_default_questions(self) -> List[str]:

        return [
            "¿Cuándo notaste el problema por primera vez?",
            "¿El problema es constante o intermitente?",
            "¿Hay algún ruido o luz de alerta?"
        ]