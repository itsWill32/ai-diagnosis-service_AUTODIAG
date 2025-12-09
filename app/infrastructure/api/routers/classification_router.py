from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.infrastructure.dependencies import (
    get_current_vehicle_owner,
    get_diagnosis_session_repository,
    get_problem_classifier_service,
    get_urgency_calculator_service,
    get_cost_estimator_service
)
from app.infrastructure.api.routers.schemas import (
    ClassificationResponse,
    UrgencyResponse,
    CostEstimateResponse,
    ErrorResponse,
    CostBreakdown
)

router = APIRouter()


@router.post(
    "/{sessionId}/classify",
    response_model=ClassificationResponse,
    summary="Clasificar problema automáticamente",
    description="Usa ML para categorizar el problema descrito"
)
async def classify_problem(
    sessionId: str,
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo = Depends(get_diagnosis_session_repository),
    classifier = Depends(get_problem_classifier_service)
):
    from datetime import datetime
    from uuid import uuid4
    
    session = await repo.find_by_id(UUID(sessionId))
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if str(session.user_id) != user["userId"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    classification = await classifier.classify_problem(session)
    
    return ClassificationResponse(
        id=str(uuid4()),
        sessionId=sessionId,
        category=classification.category.value,
        subcategory=classification.subcategory,
        confidenceScore=classification.confidence_score.value, 
        symptoms=classification.symptoms,
        createdAt=datetime.utcnow()
    )


@router.get(
    "/{sessionId}/urgency",
    response_model=UrgencyResponse,
    summary="Obtener nivel de urgencia",
    description="Determina qué tan urgente es el problema"
)
async def get_urgency_level(
    sessionId: str,
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo = Depends(get_diagnosis_session_repository),
    classifier = Depends(get_problem_classifier_service),
    urgency_calc = Depends(get_urgency_calculator_service)
):
    
    session = await repo.find_by_id(UUID(sessionId))
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if str(session.user_id) != user["userId"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    classification = await classifier.classify_problem(session)
    
    urgency_level, description, safe_to_drive, max_km = urgency_calc.calculate_urgency(classification)
    
    return UrgencyResponse(
        level=urgency_level.value,
        description=description,
        safeToDriver=safe_to_drive,
        maxMileageRecommended=max_km
    )


@router.get(
    "/{sessionId}/cost-estimate",
    response_model=CostEstimateResponse,
    summary="Obtener estimación de costos",
    description="Calcula rango de costos para la reparación"
)
async def get_cost_estimate(
    sessionId: str,
    user: Dict[str, Any] = Depends(get_current_vehicle_owner),
    repo = Depends(get_diagnosis_session_repository),
    classifier = Depends(get_problem_classifier_service),
    urgency_calc = Depends(get_urgency_calculator_service),
    cost_estimator = Depends(get_cost_estimator_service)
):
    
    session = await repo.find_by_id(UUID(sessionId))
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if str(session.user_id) != user["userId"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    classification = await classifier.classify_problem(session)
    
    urgency_level, _, _, _ = urgency_calc.calculate_urgency(classification)
    
    min_cost, max_cost, breakdown, disclaimer = cost_estimator.estimate_cost(
        classification, urgency_level
    )
    
    return CostEstimateResponse(
        minCost=min_cost,
        maxCost=max_cost,
        currency="MXN",
        breakdown=CostBreakdown(
            partsMin=breakdown["parts"]["min"],
            partsMax=breakdown["parts"]["max"],
            laborMin=breakdown["labor"]["min"],
            laborMax=breakdown["labor"]["max"]
        ),
        disclaimer=disclaimer
    )