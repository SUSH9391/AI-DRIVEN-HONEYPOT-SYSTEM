from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/honeypot"
    
    # Supabase Auth
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # ML/HF
    HF_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"  # Change to threat classifier
    HF_API_KEY: Optional[str] = None
    
    # App
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = "../.env"  # Relative from Backend/

settings = Settings()

