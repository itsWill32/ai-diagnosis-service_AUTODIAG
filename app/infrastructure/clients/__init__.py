
from .vehicle_service_client import (
    VehicleServiceClient,
    get_vehicle_service_client
)

from .workshop_service_client import (
    WorkshopServiceClient,
    get_workshop_service_client
)

from .appointment_service_client import (
    AppointmentServiceClient,
    get_appointment_service_client
)


__all__ = [

    "VehicleServiceClient",
    "get_vehicle_service_client",
    

    "WorkshopServiceClient",
    "get_workshop_service_client",
    
    "AppointmentServiceClient",
    "get_appointment_service_client",
]