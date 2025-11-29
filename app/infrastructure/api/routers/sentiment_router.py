

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.infrastructure.dependencies import (
    get_current_user,
    get_sentiment_analyzer_service,
    get_sentiment_analysis_repository
)
from app.infrastructure.api.routers.schemas import (
    AnalyzeSentimentRequest,
    SentimentAnalysisResponse,
    BatchSentimentRequest,
    SentimentResult,
    SentimentScores,
    ErrorResponse
)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=SentimentAnalysisResponse,
    summary="Analizar sentimiento de texto",
    description="Usa ML para clasificar el sentimiento (positivo/neutral/negativo)",
    responses={
        200: {"description": "Análisis completado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def analyze_sentiment(
    data: AnalyzeSentimentRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    analyzer = Depends(get_sentiment_analyzer_service),
    repo = Depends(get_sentiment_analysis_repository)
):

    from app.domain.entities.sentiment_analysis import SentimentAnalysis
    from app.domain.value_objects.sentiment_label import SentimentLabel
    
    label, confidence, scores = analyzer.analyze_sentiment(data.text)
    
    analysis = SentimentAnalysis(
        id=uuid4(),
        text=data.text,
        sentiment_label=label,
        confidence_score=confidence,
        positive_score=scores["positive"],
        neutral_score=scores["neutral"],
        negative_score=scores["negative"],
        context_data=data.context,
        analyzed_at=datetime.utcnow()
    )
    
    saved_analysis = await repo.create(analysis)
    
    return SentimentAnalysisResponse(
        id=str(saved_analysis.id),
        text=saved_analysis.text,
        sentiment=SentimentResult(
            label=saved_analysis.sentiment_label.value,
            score=saved_analysis.confidence_score,
            scores=SentimentScores(
                positive=saved_analysis.positive_score,
                neutral=saved_analysis.neutral_score,
                negative=saved_analysis.negative_score
            )
        ),
        context=saved_analysis.context_data,
        analyzedAt=saved_analysis.analyzed_at
    )


@router.post(
    "/batch",
    response_model=List[Dict[str, Any]],
    summary="Analizar sentimientos en lote",
    description="Procesa múltiples textos en una sola llamada (máx 100)",
    responses={
        200: {"description": "Análisis en lote completado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def batch_analyze_sentiment(
    data: BatchSentimentRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    analyzer = Depends(get_sentiment_analyzer_service),
    repo = Depends(get_sentiment_analysis_repository)
):

    from app.domain.entities.sentiment_analysis import SentimentAnalysis
    
    results = []
    
    for item in data.texts:
        text_id = item["id"]
        text_content = item["text"]
        
        try:
            label, confidence, scores = analyzer.analyze_sentiment(text_content)
            
            analysis = SentimentAnalysis(
                id=uuid4(),
                text=text_content,
                sentiment_label=label,
                confidence_score=confidence,
                positive_score=scores["positive"],
                neutral_score=scores["neutral"],
                negative_score=scores["negative"],
                context_data={"batch_id": text_id},
                analyzed_at=datetime.utcnow()
            )
            
            await repo.create(analysis)
            
            results.append({
                "id": text_id,
                "sentiment": {
                    "label": label.value,
                    "score": confidence,
                    "scores": {
                        "positive": scores["positive"],
                        "neutral": scores["neutral"],
                        "negative": scores["negative"]
                    }
                }
            })
            
        except Exception as e:
            results.append({
                "id": text_id,
                "error": str(e)
            })
    
    return results