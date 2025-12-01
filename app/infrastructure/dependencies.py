

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from jose import JWTError, jwt

from app.infrastructure.config.settings import get_settings
from app.infrastructure.config.database import get_prisma_client

from app.infrastructure.repositories import (
    PrismaDiagnosisSessionRepository,
    PrismaProblemClassificationRepository,
    PrismaSentimentAnalysisRepository
)

from app.infrastructure.services import (
    GeminiService,
    ProblemClassifierService,
    UrgencyCalculatorService,
    CostEstimatorService,
    SentimentAnalyzerService
)

from app.infrastructure.clients import (
    get_vehicle_service_client,
    get_workshop_service_client
)




async def get_current_user(
    authorization: str = Header(..., description="JWT token en formato: Bearer <token>")
) -> Dict[str, Any]:
    
    settings = get_settings()
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")  
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if not user_id or not email or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            "userId": user_id, 
            "email": email,
            "role": role
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:

    if current_user["role"] != "SYSTEM_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )
    
    return current_user


async def get_current_workshop_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:

    if current_user["role"] not in ["WORKSHOP_ADMIN", "SYSTEM_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores de taller pueden acceder a este endpoint"
        )
    
    return current_user


async def get_current_vehicle_owner(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
 
    if current_user["role"] not in ["VEHICLE_OWNER", "SYSTEM_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo propietarios de vehículo pueden acceder a este endpoint"
        )
    
    return current_user




def get_diagnosis_session_repository() -> PrismaDiagnosisSessionRepository:

    prisma = get_prisma_client()
    return PrismaDiagnosisSessionRepository(prisma)


def get_problem_classification_repository() -> PrismaProblemClassificationRepository:

    prisma = get_prisma_client()
    return PrismaProblemClassificationRepository(prisma)


def get_sentiment_analysis_repository() -> PrismaSentimentAnalysisRepository:

    prisma = get_prisma_client()
    return PrismaSentimentAnalysisRepository(prisma)




def get_gemini_service() -> GeminiService:

    return GeminiService()


def get_problem_classifier_service() -> ProblemClassifierService:

    return ProblemClassifierService()


def get_urgency_calculator_service() -> UrgencyCalculatorService:

    return UrgencyCalculatorService()


def get_cost_estimator_service() -> CostEstimatorService:
 
    return CostEstimatorService()


def get_sentiment_analyzer_service() -> SentimentAnalyzerService:

    return SentimentAnalyzerService()




def get_vehicle_client():

    return get_vehicle_service_client()


def get_workshop_client():

    return get_workshop_service_client()



__all__ = [

    "get_current_user",
    "get_current_admin_user",
    "get_current_workshop_admin",
    "get_current_vehicle_owner",
    

    "get_diagnosis_session_repository",
    "get_problem_classification_repository",
    "get_sentiment_analysis_repository",
    

    "get_gemini_service",
    "get_problem_classifier_service",
    "get_urgency_calculator_service",
    "get_cost_estimator_service",
    "get_sentiment_analyzer_service",
    

    "get_vehicle_client",
    "get_workshop_client",
]