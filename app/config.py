import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./arthaya.db"
    
    # n8n Orchestrator Integration
    N8N_BASE_URL: str = "https://n8n.sushantkumaryadav.com.np"
    N8N_WEBHOOK_URL: str = "https://n8n.sushantkumaryadav.com.np/webhook/arthaya-orchestrator"
    N8N_API_KEY: str = ""
    
    # Model Gateway API Keys
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
