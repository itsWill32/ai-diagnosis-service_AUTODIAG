

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.infrastructure.config.settings import get_settings
from app.infrastructure.config.database import initialize_database, close_database
from app.infrastructure.middleware import (
    setup_error_handlers,
    request_logging_middleware
)

from app.infrastructure.api.routers import (
    diagnosis_router,
    classification_router,
    recommendations_router,
    sentiment_router,
    analytics_router
)



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("STARTING  SERVICE")
    
    settings = get_settings()
    
    try:
        await initialize_database()
        logger.info(" DB Connected")
    except Exception as e:
        logger.error(f" DB failed: {str(e)}")
        raise
    
    logger.info(f" Redis: Connected to {settings.REDIS_URL.split('@')[1] if '@' in settings.REDIS_URL else 'Redis'}")
    logger.info(" SERVICE READY")
    
    yield
    
    logger.info("SHUTTING DOWN SERVICE")
    
    try:
        await close_database()
        logger.info("DB Disconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    
    logger.info("SHUTDOWN COMPLETE")



app = FastAPI(
    title="AutoDiag - Diagnosis Service API",
    version="1.0.0",
    lifespan=lifespan,  

)




settings = get_settings()

allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else [
    "http://localhost:3000",  
    "http://localhost:8080",  
    "https://warm-crisp-f80a0b.netlify.app",
    "'http://localhost:5173" 

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)




setup_error_handlers(app)



@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Verifica que el servicio está funcionando correctamente",
    response_description="Estado del servicio"
)
async def health_check():
    from app.infrastructure.config.database import check_database_health
    
    db_health = await check_database_health()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "service": "diagnosis-service",
        "version": "1.0.0",
        "database": db_health
    }


@app.get(
    "/",
    tags=["Root"],
    summary="Service Info",
    description="Información básica del servicio"
)
async def root():
    return {
        "service": "AutoDiag - Diagnosis Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    error_message = "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": error_message,
            "statusCode": 500
        }
    )



app.include_router(
    diagnosis_router,
    prefix="/sessions",
    tags=["Diagnosis"]
)

app.include_router(
    classification_router,
    prefix="/sessions",
    tags=["Classification"]
)

app.include_router(
    recommendations_router,
    prefix="/sessions",
    tags=["Recommendations"]
)

app.include_router(
    sentiment_router,
    prefix="/sentiment",
    tags=["Sentiment"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)




if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",
        port=settings.PORT,
        reload=False, 
        log_level="info"
    )