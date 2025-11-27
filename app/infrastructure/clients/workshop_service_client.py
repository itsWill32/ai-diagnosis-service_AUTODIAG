
from typing import Optional, Dict, Any, List
import httpx

from app.infrastructure.config.settings import get_settings
from app.domain.value_objects.problem_category import ProblemCategory


class WorkshopServiceClient:

    
    def __init__(self):

        self.settings = get_settings()
        self.base_url = self.settings.WORKSHOP_SERVICE_URL
        self.timeout = 10.0
    
    async def get_workshop(
        self,
        workshop_id: str,
        auth_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:

        url = f"{self.base_url}/workshops/{workshop_id}"
        
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = auth_token
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError:
            return None
    
    async def search_nearby_workshops(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        specialty: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        url = f"{self.base_url}/search/nearby"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radiusKm": radius_km,
            "limit": limit
        }
        
        if specialty:
            params["specialtyType"] = specialty
        
        if min_rating:
            params["minRating"] = min_rating
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    return []
                
                return response.json()
                
        except httpx.HTTPError:
            return []
    
    async def get_workshops_by_specialty(
        self,
        specialty: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        if latitude and longitude:
            return await self.search_nearby_workshops(
                latitude=latitude,
                longitude=longitude,
                specialty=specialty,
                limit=limit
            )
        
        url = f"{self.base_url}/workshops"
        
        params = {
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    return []
                
                workshops = response.json().get("workshops", [])
                
                filtered = []
                for workshop in workshops:
                    specialties = workshop.get("specialties", [])
                    has_specialty = any(
                        s.get("specialtyType") == specialty 
                        for s in specialties
                    )
                    
                    if has_specialty:
                        filtered.append(workshop)
                    
                    if len(filtered) >= limit:
                        break
                
                return filtered
                
        except httpx.HTTPError:
            return []
    
    async def get_workshop_reviews(
        self,
        workshop_id: str,
        limit: int = 10,
        sort_by: str = "recent"
    ) -> List[Dict[str, Any]]:

        url = f"{self.base_url}/workshops/{workshop_id}/reviews"
        
        params = {
            "limit": limit,
            "sortBy": sort_by
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                
                if isinstance(data, dict):
                    return data.get("reviews", [])
                
                return data
                
        except httpx.HTTPError:
            return []
    
    async def get_workshop_rating(
        self,
        workshop_id: str
    ) -> Optional[float]:

        workshop = await self.get_workshop(workshop_id)
        
        if not workshop:
            return None
        
        return workshop.get("overallRating")
    
    async def validate_workshop_exists(
        self,
        workshop_id: str
    ) -> bool:

        workshop = await self.get_workshop(workshop_id)
        return workshop is not None
    
    async def get_workshop_specialties(
        self,
        workshop_id: str
    ) -> List[str]:

        workshop = await self.get_workshop(workshop_id)
        
        if not workshop:
            return []
        
        specialties_list = workshop.get("specialties", [])
        
        return [
            s.get("specialtyType") 
            for s in specialties_list 
            if s.get("specialtyType")
        ]


_client_instance: Optional[WorkshopServiceClient] = None

def get_workshop_service_client() -> WorkshopServiceClient:

    global _client_instance
    
    if _client_instance is None:
        _client_instance = WorkshopServiceClient()
    
    return _client_instance