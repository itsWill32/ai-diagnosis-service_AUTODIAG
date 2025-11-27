

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    
    PORT: int = 3004
    
    DATABASE_URL: str
    
    REDIS_URL: str
    
    GOOGLE_GEMINI_API_KEY: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    VEHICLE_SERVICE_URL: Optional[str] = "http://localhost:3002"
    WORKSHOP_SERVICE_URL: Optional[str] = "http://localhost:3003"
    
    ALLOWED_ORIGINS: str = "http://localhost:8080,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()