# ============================================
# AI-DIAGNOSIS SERVICE - MAIN
# FastAPI Entry Point
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AutoDiag - AI Diagnosis Service",
    description="Servicio de diagnóstico con IA usando Google Gemini",
    version="1.0.0-mvp"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-diagnosis-service",
        "version": "1.0.0-mvp"
    }

# Root
@app.get("/")
def root():
    return {
        "message": "AutoDiag AI Diagnosis Service",
        "docs": "/docs"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3005))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENV") == "development" else False
    )