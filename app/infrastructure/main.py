
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.infrastructure.config.settings import get_settings
from app.infrastructure.middleware import (
    setup_error_handlers,
    request_logging_middleware
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
    
    logger.info(f"🔌 Port: {settings.PORT}")
    logger.info(f"🗄️  Database: Connected to PostgreSQL")
    logger.info(f"🔴 Redis: Connected to {settings.REDIS_URL.split('@')[1] if '@' in settings.REDIS_URL else 'Redis'}")
    
    logger.info("SERVICE READY ")
    

    
    yield
    
    logger.info("SHUTTING DOWN  SERVICE")

    



app = FastAPI(
    title="AutoDiag - Diagnosis Service API",
    
    version="1.0.0"
)


settings = get_settings()

allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else [
    "http://localhost:3000",  
    "http://localhost:8080",  
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

    return {
        "status": "healthy",
        "service": "diagnosis-service",
        "version": "1.0.0",
        "environment": settings.NODE_ENV
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




if __name__ == "__main__":
    import uvicorn
    

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False, 
        log_level="info"
    )