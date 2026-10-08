from fastapi import APIRouter

router = APIRouter(prefix="/data-sources", tags=["data-sources"])

@router.get("")
async def get_data_sources():
    return {
        "data": [
            {"provider": "yfinance", "dataType": "Market Data & OHLCV", "status": "connected", "coverage": "Global Equities & Indices"},
            {"provider": "SEC EDGAR", "dataType": "Financial Filings & 10-K/10-Q", "status": "connected", "coverage": "US Public Companies"},
            {"provider": "n8n Orchestrator", "dataType": "Agentic Workflow Trigger (n8n.sushantkumaryadav.com.np)", "status": "connected", "coverage": "Parallel Agent Grid"},
            {"provider": "Firecrawl", "dataType": "Clean Web Crawling & Article Markdown", "status": "configured", "coverage": "Financial News Sites"},
            {"provider": "Apify", "dataType": "Structured Actor Scraper", "status": "configured", "coverage": "Web Intelligence"},
            {"provider": "Model Gateway", "dataType": "Claude / Gemini / Mistral / Groq / OpenRouter", "status": "connected", "coverage": "Multi-Model LLM Synthesis"},
        ],
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }
