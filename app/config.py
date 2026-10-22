import os
import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Optional

class Settings(BaseSettings):
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PUBLIC_URL: str = ""
    RENDER_EXTERNAL_URL: Optional[str] = None
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://arthaya.vercel.app"
    ]
    
    # Database Configuration (PostgreSQL / SQLite fallback)
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

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def EFFECTIVE_PUBLIC_URL(self) -> str:
        if self.PUBLIC_URL:
            return self.PUBLIC_URL.rstrip("/")
        if self.RENDER_EXTERNAL_URL:
            return self.RENDER_EXTERNAL_URL.rstrip("/")
        return f"http://{self.HOST}:{self.PORT}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
