from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database - Read from environment variable, fallback to default
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/water_inventory"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Support local development, Vercel frontend, and Railway
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add your Vercel frontend domain here after deployment
        # "https://your-frontend.vercel.app"
    ]
    
    # Allow dynamic CORS origins via environment variable
    ADDITIONAL_CORS_ORIGINS: List[str] = []
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Add any additional CORS origins from environment variable
if os.getenv("VERCEL_URL"):
    settings.CORS_ORIGINS.append(f"https://{os.getenv('VERCEL_URL')}")
if os.getenv("ADDITIONAL_CORS_ORIGINS"):
    additional = os.getenv("ADDITIONAL_CORS_ORIGINS", "").split(",")
    settings.CORS_ORIGINS.extend([origin.strip() for origin in additional if origin.strip()])
