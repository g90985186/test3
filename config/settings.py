from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - using SQLite for development
    database_url: str = "sqlite:///./cve_platform.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Ollama
    ollama_url: str = "http://localhost:11434"
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs
    nvd_api_key: Optional[str] = None
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # CORS Origins
    CORS_ORIGINS: list = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
