"""
Cliente HTTP para comunicarse con el Appointment Service.
"""

from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime


class AppointmentServiceClient:
    """
    Cliente para interactuar con el microservicio de citas (appointment-service).
    """
    
    def __init__(self, base_url: str = "https://appointment-service-autodiag.onrender.com/api"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 10.0
    
    async def get_all_appointments(
        self,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        admin_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las citas del sistema (requiere permisos de admin).
        
        Args:
            status: Filtrar por estado (PENDING, CONFIRMED, etc.)
            from_date: Fecha inicio (YYYY-MM-DD)
            to_date: Fecha fin (YYYY-MM-DD)
            admin_token: Token JWT del admin
            
        Returns:
            Lista de citas
        """
        try:
            params = {}
            if status:
                params["status"] = status
            if from_date:
                params["fromDate"] = from_date
            if to_date:
                params["toDate"] = to_date
            
            headers = {}
            if admin_token:
                headers["Authorization"] = f"Bearer {admin_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/appointments",
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error obteniendo citas: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"Error en AppointmentServiceClient.get_all_appointments: {e}")
            return []
    
    async def count_appointments(
        self,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        admin_token: Optional[str] = None
    ) -> int:
        """
        Cuenta el total de citas en el sistema.
        
        Args:
            status: Filtrar por estado
            from_date: Fecha inicio
            to_date: Fecha fin
            admin_token: Token JWT del admin
            
        Returns:
            Número total de citas
        """
        appointments = await self.get_all_appointments(
            status=status,
            from_date=from_date,
            to_date=to_date,
            admin_token=admin_token
        )
        return len(appointments)
    
    async def get_workshop_appointments(
        self,
        workshop_id: str,
        status: Optional[str] = None,
        date: Optional[str] = None,
        admin_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene citas de un taller específico.
        
        Args:
            workshop_id: ID del taller
            status: Filtrar por estado
            date: Fecha específica (YYYY-MM-DD)
            admin_token: Token JWT del admin
            
        Returns:
            Lista de citas del taller
        """
        try:
            params = {}
            if status:
                params["status"] = status
            if date:
                params["date"] = date
            
            headers = {}
            if admin_token:
                headers["Authorization"] = f"Bearer {admin_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/workshops/{workshop_id}/appointments",
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error obteniendo citas del taller: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"Error en AppointmentServiceClient.get_workshop_appointments: {e}")
            return []


def get_appointment_service_client() -> AppointmentServiceClient:
    """
    Factory function para obtener instancia del cliente de appointments.
    """
    return AppointmentServiceClient()
