from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.infrastructure.config.settings import get_settings
from app.infrastructure.config.database import get_db
from app.infrastructure.middleware import (
    setup_error_handlers,
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

    
    settings = get_settings()
    

    try:
        db = await get_db()
        await db.connect()
        logger.info("Db connected ")
        
        result = await db.query_raw("SELECT COUNT(*) FROM diagnosis_sessions")
        logger.info(f"📊 Found {result[0]['count']} sessions in database")
        
    except Exception as e:
        logger.error(f" Database connection failed: {str(e)}")
        raise
    
    logger.info(" DIAGNOSIS SERVICE READY")
    
    yield
    

    logger.info("SHUTTING DOWN DIAGNOSIS SERVICE...")
    
    try:
        db = await get_db()
        await db.disconnect()
        logger.info(" Database disconnected successfully")
    except Exception as e:
        logger.error(f" Error during shutdown: {str(e)}")
    
    logger.info(" SHUTDOWN COMPLETE")



app = FastAPI(
    title="AutoDiag - Diagnosis Service API",
    description="  AutoDiag Diagnosis Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


settings = get_settings()

allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://warm-crisp-f80a0b.netlify.app",
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
    """
    Endpoint de health check que verifica:
    - Estado del servicio
    - Conexión a base de datos
    - Versión del servicio
    """
    try:
        db = await get_db()
        
        await db.query_raw("SELECT 1")
        db_status = "healthy"
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "diagnosis-service",
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "provider": "postgresql"
        }
    }

@app.get(
    "/",
    tags=["Root"],
    summary="Service Info",
    description="Información básica del servicio"
)
async def root():
    """
    Endpoint raíz con información del servicio.
    """
    return {
        "service": "AutoDiag - Diagnosis Service",
        "version": "1.0.0",
        "description": "Servicio de diagnóstico automotriz con IA",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones no capturadas.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
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
        reload=True,
        log_level="info"
    )