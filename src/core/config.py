from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = 5432
    dbname: Optional[str] = "postgres"
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
    
    @model_validator(mode='after')
    def construct_supabase_url(self) -> 'Settings':
        if self.host and self.user and "localhost" in self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?sslmode=require"
        return self

    class Config:
        env_file = ".env"  # Project root

settings = Settings()

