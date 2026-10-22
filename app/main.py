from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.v1.router import api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization
    try:
        await init_db()
        print("✅ Database tables initialized successfully.")
    except Exception as e:
        print(f"⚠️ DB Initialization notice: {e}")
    yield

app = FastAPI(
    title="Arthaya — Multi-Agent Financial Intelligence API",
    description="High-performance backend API powering Arthaya multi-agent, multi-model equity research and quant predictions.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend (local dev, production, custom domain, and Vercel preview deployments)
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https:\/\/(.*\.)?(vercel\.app|sushantkumaryadav\.com\.np)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Arthaya Financial Intelligence Backend",
        "env": settings.ENV,
        "public_url": settings.EFFECTIVE_PUBLIC_URL,
        "n8n_orchestrator": settings.N8N_BASE_URL,
        "n8n_webhook": settings.N8N_WEBHOOK_URL,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
