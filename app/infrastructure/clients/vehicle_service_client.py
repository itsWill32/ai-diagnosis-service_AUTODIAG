from typing import Optional, Dict, Any, Union
import httpx
from datetime import datetime
from uuid import UUID

from app.infrastructure.config.settings import get_settings


class VehicleServiceClient:
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.VEHICLE_SERVICE_URL
        self.timeout = 20.0
        
    async def get_vehicle(
        self,
        vehicle_id: str,
        user_id: str,
        auth_token: str
    ) -> Optional[Dict[str, Any]]:

        url = f"{self.base_url}/vehicles/{vehicle_id}"
        
        if auth_token and not auth_token.startswith("Bearer "):
            auth_token = f"Bearer {auth_token}"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AutoDiag-DiagnosisService/1.0"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 404:
                    return None
                
                if response.status_code in [401, 403]:
                    print(f"DEBUG: Vehicle Auth Error {response.status_code}")
                    return None
                
                response.raise_for_status()
                
                vehicle = response.json()
                
                if vehicle.get("ownerId") != user_id:
                    return None
                
                return vehicle
                
        except Exception as e:
            print(f"DEBUG: Vehicle Service Error: {e}")
            return None
    
    async def validate_vehicle_ownership(
        self,
        vehicle_id: str,
        user_id: str,
        auth_token: str
    ) -> bool:
        try:
            vehicle = await self.get_vehicle(vehicle_id, user_id, auth_token)
            return vehicle is not None
        except Exception:
            return False

    async def vehicle_exists(
        self, 
        vehicle_id: Union[UUID, str], 
        user_id: Union[UUID, str],
        token: str
    ) -> bool:
        return await self.validate_vehicle_ownership(
            vehicle_id=str(vehicle_id),
            user_id=str(user_id),
            auth_token=token
        )

    async def create_maintenance_record(
        self,
        vehicle_id: str,
        diagnosis_data: Dict[str, Any],
        auth_token: str
    ) -> Optional[Dict[str, Any]]:

        url = f"{self.base_url}/vehicles/{vehicle_id}/maintenance"
        
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "serviceType": diagnosis_data.get("serviceType", "OTHER"),
            "description": diagnosis_data.get("description", "Diagnóstico AutoDiag"),
            "serviceDate": datetime.now().strftime("%Y-%m-%d"),
            "mileageAtService": diagnosis_data.get("mileage", 0),
            "cost": diagnosis_data.get("cost"),
            "currency": "MXN",
            "workshopName": diagnosis_data.get("workshopName"),
            "notes": diagnosis_data.get("notes")
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 201:
                    return None
                
                return response.json()
                
        except Exception:
            return None
    
    async def get_vehicle_mileage(
        self,
        vehicle_id: str,
        auth_token: str
    ) -> Optional[int]:

        url = f"{self.base_url}/vehicles/{vehicle_id}"
        
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    return None
                
                vehicle = response.json()
                return vehicle.get("currentMileage")
                
        except Exception:
            return None


_client_instance: Optional[VehicleServiceClient] = None

def get_vehicle_service_client() -> VehicleServiceClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = VehicleServiceClient()
    return _client_instance