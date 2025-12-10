
import math
from typing import List, Dict, Any, Optional
from app.domain.value_objects import ProblemCategory


class WorkshopRecommenderService:

    CATEGORY_TO_SPECIALTY_MAP = {
        "ENGINE": "MOTOR",
        "TRANSMISSION": "TRANSMISION",
        "BRAKES": "FRENOS",
        "ELECTRICAL": "ELECTRICO",
        "AIR_CONDITIONING": "AIRE_ACONDICIONADO",
        "SUSPENSION": "SUSPENSION",
        "EXHAUST": "ESCAPE",
        "FUEL_SYSTEM": "SISTEMA_COMBUSTIBLE",
        "COOLING_SYSTEM": "SISTEMA_ENFRIAMIENTO",
        "TIRES": "NEUMATICOS",
        "BATTERY": "BATERIA",
        "LIGHTS": "LUCES",
        "OTHER": "GENERAL"
    }
    
    WEIGHT_SPECIALIZATION = 0.40
    WEIGHT_PROXIMITY = 0.35
    WEIGHT_RATING = 0.25
    
    DEFAULT_SEARCH_RADIUS_KM = 50.0
    
    def __init__(self, workshop_client=None):

        self.workshop_client = workshop_client
    
    async def recommend_workshops(
        self,
        category: str,
        user_location: Dict[str, float],
        limit: int = 3,
        max_radius_km: float = None
    ) -> List[Dict[str, Any]]:

        if not self.workshop_client:
            return []
        
        if not user_location or "latitude" not in user_location or "longitude" not in user_location:
            return []
        
        user_lat = user_location["latitude"]
        user_lon = user_location["longitude"]
        
        specialty_type = self._map_category_to_specialty(category)
        
        radius_km = max_radius_km or self.DEFAULT_SEARCH_RADIUS_KM
        
        try:
            nearby_workshops = await self.workshop_client.search_nearby_workshops(
                latitude=user_lat,
                longitude=user_lon,
                radius_km=radius_km,
                specialty=specialty_type,
                limit=limit * 3  
            )
        except Exception as e:
            print(f"Error buscando talleres: {e}")
            return []
        
        if not nearby_workshops:
            return []
        
        recommendations = []
        
        for workshop in nearby_workshops:
            workshop_id = workshop.get("id")
            workshop_lat = workshop.get("latitude")
            workshop_lon = workshop.get("longitude")
            workshop_rating = workshop.get("overallRating", 0.0)
            workshop_name = workshop.get("businessName", "Taller")
            specialties = workshop.get("specialties", [])
            
            if not workshop_id or workshop_lat is None or workshop_lon is None:
                continue
            
            distance_km = self._haversine_distance(
                user_lat, user_lon,
                workshop_lat, workshop_lon
            )
            
            match_score = self._calculate_match_score(
                specialties=specialties,
                target_specialty=specialty_type,
                distance_km=distance_km,
                rating=workshop_rating,
                max_radius_km=radius_km
            )
            
            reasons = self._generate_reasons(
                specialties=specialties,
                target_specialty=specialty_type,
                distance_km=distance_km,
                rating=workshop_rating
            )
            
            recommendations.append({
                "workshop_id": workshop_id,
                "workshop_name": workshop_name,
                "match_score": match_score,
                "distance_km": round(distance_km, 2),
                "rating": workshop_rating,
                "reasons": reasons
            })
        
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return recommendations[:limit]
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:

        R = 6371.0
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return distance
    
    def _calculate_match_score(
        self,
        specialties: List[Dict[str, Any]],
        target_specialty: str,
        distance_km: float,
        rating: float,
        max_radius_km: float
    ) -> float:

        # 1. Specialization Score (40%)
        specialization_score = self._calculate_specialization_score(
            specialties, target_specialty
        )
        
        # 2. Proximity Score (35%)
        proximity_score = self._calculate_proximity_score(
            distance_km, max_radius_km
        )
        
        # 3. Rating Score (25%)
        rating_score = self._calculate_rating_score(rating)
        
        match_score = (
            self.WEIGHT_SPECIALIZATION * specialization_score +
            self.WEIGHT_PROXIMITY * proximity_score +
            self.WEIGHT_RATING * rating_score
        )
        
        return round(match_score, 3)
    
    def _calculate_specialization_score(
        self,
        specialties: List[Dict[str, Any]],
        target_specialty: str
    ) -> float:
        """
        Calcula el score de especialización.
        
        Returns:
            1.0 si tiene la especialidad exacta
            0.5 si tiene especialidades relacionadas
            0.0 si no tiene especialidades relevantes
        """
        if not specialties:
            return 0.0
        
        specialty_types = [s.get("specialtyType") for s in specialties if s.get("specialtyType")]
        
        if target_specialty in specialty_types:
            return 1.0
        
        if "GENERAL" in specialty_types:
            return 0.5
        
        return 0.0
    
    def _calculate_proximity_score(
        self,
        distance_km: float,
        max_radius_km: float
    ) -> float:
        """
        Calcula el score de proximidad (más cerca = mejor).
        
        Returns:
            1.0 si está muy cerca (< 5 km)
            Decae linealmente hasta 0.0 en max_radius_km
        """
        if distance_km <= 5.0:
            return 1.0
        
        if distance_km >= max_radius_km:
            return 0.0
        
        score = 1.0 - ((distance_km - 5.0) / (max_radius_km - 5.0))
        
        return max(0.0, min(1.0, score))
    
    def _calculate_rating_score(self, rating: float) -> float:
        """
        Calcula el score de rating.
        
        Args:
            rating: Rating de 0.0 a 5.0
            
        Returns:
            Score normalizado de 0.0 a 1.0
        """
        if rating <= 0:
            return 0.0
        
        # Normalizar de 0-5 a 0-1
        return min(rating / 5.0, 1.0)
    
    def _map_category_to_specialty(self, category: str) -> str:

        return self.CATEGORY_TO_SPECIALTY_MAP.get(category, "GENERAL")
    
    def _generate_reasons(
        self,
        specialties: List[Dict[str, Any]],
        target_specialty: str,
        distance_km: float,
        rating: float
    ) -> List[str]:
        """
        Genera razones legibles de por qué se recomienda este taller.
        
        Returns:
            Lista de razones (strings)
        """
        reasons = []
        
        # Razón de especialización
        specialty_types = [s.get("specialtyType") for s in specialties if s.get("specialtyType")]
        
        if target_specialty in specialty_types:
            specialty_name = self._get_specialty_display_name(target_specialty)
            reasons.append(f"Especializado en {specialty_name}")
        elif "GENERAL" in specialty_types:
            reasons.append("Taller de servicio general")
        
        # Razón de proximidad
        if distance_km < 5.0:
            reasons.append(f"Muy cerca: {distance_km:.1f} km")
        elif distance_km < 15.0:
            reasons.append(f"Cercano: {distance_km:.1f} km")
        else:
            reasons.append(f"A {distance_km:.1f} km de distancia")
        
        # Razón de rating
        if rating >= 4.5:
            reasons.append(f"Excelente calificación: {rating:.1f}★")
        elif rating >= 4.0:
            reasons.append(f"Buena calificación: {rating:.1f}★")
        elif rating >= 3.0:
            reasons.append(f"Calificación: {rating:.1f}★")
        
        return reasons
    

        display_names = {
            "MOTOR": "problemas de motor",
            "TRANSMISION": "transmisión",
            "FRENOS": "frenos",
            "ELECTRICO": "sistema eléctrico",
            "AIRE_ACONDICIONADO": "aire acondicionado",
            "SUSPENSION": "suspensión",
            "ESCAPE": "sistema de escape",
            "SISTEMA_COMBUSTIBLE": "sistema de combustible",
            "SISTEMA_ENFRIAMIENTO": "sistema de enfriamiento",
            "NEUMATICOS": "neumáticos",
            "BATERIA": "batería",
            "LUCES": "luces",
            "GENERAL": "servicio general"
        }
        
        return display_names.get(specialty_type, specialty_type.lower())


_service_instance: Optional[WorkshopRecommenderService] = None


def get_workshop_recommender_service(workshop_client=None) -> WorkshopRecommenderService:

    global _service_instance
    
    if _service_instance is None or workshop_client is not None:
        _service_instance = WorkshopRecommenderService(workshop_client)
    
    return _service_instance
