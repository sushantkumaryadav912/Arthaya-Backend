from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("")
async def get_agent_status():
    return {
        "data": [
            {"id": "orchestrator", "name": "n8n Orchestrator", "role": "Workflow Planner & Coordinator", "status": "idle", "description": "Dispatches tools, coordinates shared state, and handles retries."},
            {"id": "market", "name": "Market Data Agent", "role": "Raw Market Quotes & OHLCV", "status": "idle", "description": "Fetches price quotes, volume, market cap, and trading metrics."},
            {"id": "technical", "name": "Technical Analysis Agent", "role": "Technical Indicator Calculation", "status": "idle", "description": "Computes RSI, MACD, Moving Averages, ATR, and Bollinger Bands."},
            {"id": "fundamental", "name": "Fundamental Agent", "role": "Financial Statements & Ratios", "status": "idle", "description": "Analyzes revenue, income, cash flows, valuation, and leverage."},
            {"id": "news", "name": "News & Sentiment Agent", "role": "Web Intelligence & NLP Scoring", "status": "idle", "description": "Processes news feeds, event classification, and sentiment scores."},
            {"id": "historical", "name": "Historical Analogs Agent", "role": "Regime Matching & Forward Returns", "status": "idle", "description": "Matches current feature vector to historical market regimes."},
            {"id": "prediction", "role": "Quant Predictive Layer", "name": "Prediction Agent", "status": "idle", "description": "Runs LR, Random Forest, and XGBoost machine-learning models."},
            {"id": "critic", "name": "Adversarial Critic Agent", "role": "Quality Validation & Leakage Check", "status": "idle", "description": "Validates data freshness, source quality, signal agreement, and zero leakage."},
            {"id": "synthesis", "name": "Synthesis Agent", "role": "Model Gateway LLM Synthesis", "status": "idle", "description": "Reconciles findings and generates explainable research reports via Model Gateway."},
        ],
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }
