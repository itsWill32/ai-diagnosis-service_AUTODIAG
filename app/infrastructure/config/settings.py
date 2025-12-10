

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):

    PORT: int = 3004
    
    DATABASE_URL: str
    
    REDIS_URL: str
    
    GOOGLE_GEMINI_API_KEY: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    VEHICLE_SERVICE_URL: Optional[str] = "https://vehicle-service-autodiag.onrender.com"
    WORKSHOP_SERVICE_URL: Optional[str] = "https://workshop-service-autodiag.onrender.com"
    
    ALLOWED_ORIGINS: str = "http://localhost:8080,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins(self) -> list[str]:

        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:

    return Settings()


settings = get_settings()