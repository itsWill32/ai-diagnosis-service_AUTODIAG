

from .diagnosis_router import router as diagnosis_router
from .classification_router import router as classification_router
from .recommendations_router import router as recommendations_router
from .sentiment_router import router as sentiment_router
from .analytics_router import router as analytics_router


__all__ = [
    "diagnosis_router",
    "classification_router",
    "recommendations_router",
    "sentiment_router",
    "analytics_router",
]