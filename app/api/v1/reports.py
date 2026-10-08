from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("")
async def list_reports():
    return {
        "data": [
            {
                "id": "rep_aapl_5d_01",
                "ticker": "AAPL",
                "companyName": "Apple Inc.",
                "title": "AAPL 5-Day Multi-Agent Intelligence Synthesis",
                "createdAt": "2026-10-08T09:00:00Z",
                "horizon": "5D",
                "overallSignal": "UP",
                "probability": 0.68,
                "confidence": "Medium-High",
                "modelName": "XGBoost v1.3",
            },
            {
                "id": "rep_nvda_5d_02",
                "ticker": "NVDA",
                "companyName": "NVIDIA Corporation",
                "title": "NVDA 5-Day Multi-Agent Intelligence Synthesis",
                "createdAt": "2026-10-07T16:30:00Z",
                "horizon": "5D",
                "overallSignal": "UP",
                "probability": 0.61,
                "confidence": "Moderate",
                "modelName": "XGBoost v1.3",
            },
        ],
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }

@router.get("/{report_id}")
async def get_report_detail(report_id: str):
    return {
        "data": {
            "id": report_id,
            "ticker": "AAPL",
            "companyName": "Apple Inc.",
            "title": "AAPL 5-Day Multi-Agent Intelligence Synthesis",
            "createdAt": "2026-10-08T09:00:00Z",
            "horizon": "5D",
            "overallSignal": "UP",
            "probability": 0.68,
            "confidence": "Medium-High",
            "modelName": "XGBoost v1.3",
            "summary": "AAPL exhibits moderately positive technical momentum and supportive news sentiment...",
            "contentMarkdown": "# Executive Summary\n\nAAPL exhibits moderately positive technical momentum...",
            "sections": [
                {"title": "Executive Summary", "content": "AAPL exhibits moderately positive technical momentum..."},
                {"title": "Market Context", "content": "Trading at $224.50 (+1.25%)..."},
            ],
            "sources": [
                {"name": "Yahoo Finance Market Data API", "kind": "market-data", "url": "https://finance.yahoo.com"},
                {"name": "SEC EDGAR Filings", "kind": "market-data", "url": "https://sec.gov"},
            ]
        },
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }
