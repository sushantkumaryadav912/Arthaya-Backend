from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.market_service import MarketService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService
from app.services.news_service import NewsService
from app.services.historical_service import HistoricalService
from app.services.feature_builder import FeatureBuilder
from app.services.ml_engine import MLEngine
from app.services.critic_service import CriticService
from app.services.model_gateway import ModelGateway
from app.services.n8n_client import N8NClient

router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisStartRequest(BaseModel):
    ticker: str
    horizon: str = "5D"
    depth: str = "standard"
    gateway_provider: str = "claude"

# In-memory analysis cache for real-time streaming
ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}

@router.post("")
async def start_analysis(req: AnalysisStartRequest):
    analysis_id = f"ana_{uuid.uuid4().hex[:10]}"
    
    # Notify n8n Orchestrator at n8n.sushantkumaryadav.com.np
    n8n_response = await N8NClient.trigger_analysis_workflow(
        analysis_id=analysis_id,
        ticker=req.ticker,
        horizon=req.horizon,
        depth=req.depth,
        gateway_provider=req.gateway_provider
    )

    ANALYSIS_CACHE[analysis_id] = {
        "analysisId": analysis_id,
        "ticker": req.ticker.upper(),
        "horizon": req.horizon,
        "depth": req.depth,
        "gatewayProvider": req.gateway_provider,
        "status": "queued",
        "createdAt": datetime.utcnow().isoformat(),
        "n8n": n8n_response
    }

    return {"analysis_id": analysis_id, "status": "queued", "n8n": n8n_response}

@router.get("/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    if analysis_id in ANALYSIS_CACHE and "run" in ANALYSIS_CACHE[analysis_id]:
        return {"data": ANALYSIS_CACHE[analysis_id]["run"], "demo": True, "generatedAt": datetime.utcnow().isoformat()}
    
    # Generate on-demand if missing
    run_data = await _execute_pipeline("AAPL", "5D", "standard", "claude", analysis_id)
    return {"data": run_data, "demo": True, "generatedAt": datetime.utcnow().isoformat()}

@router.get("/{analysis_id}/stream")
async def stream_analysis_events(analysis_id: str, ticker: str = "AAPL", horizon: str = "5D", depth: str = "standard", gateway: str = "claude"):
    """Server-Sent Events (SSE) streaming endpoint for real-time agent execution."""
    async def event_generator():
        agents = [
            ("orchestrator", "Initializing n8n multi-agent pipeline"),
            ("market", "Collecting market quotes & OHLCV data"),
            ("technical", "Calculating RSI, MACD, SMAs, & Bollinger bands"),
            ("fundamental", "Analyzing income statements, balance sheets, and ratios"),
            ("news", "Extracting web news articles & scoring sentiment"),
            ("historical", "Searching historical analogue regimes"),
            ("prediction", "Running Layer 2 Quant ML (LR / RF / XGBoost)"),
            ("critic", "Executing adversarial quality & data leakage checks"),
            ("synthesis", f"Generating research synthesis via Model Gateway ({gateway.upper()})"),
        ]

        total = len(agents)
        for i, (agent_id, msg) in enumerate(agents):
            await asyncio.sleep(0.4) # Simulate async processing
            event_payload = {
                "analysisId": analysis_id,
                "agent": agent_id,
                "status": "completed",
                "message": msg,
                "progress": int(((i + 1) / total) * 100),
                "timestamp": datetime.utcnow().isoformat(),
                "clock": f"00:0{i+1}",
            }
            yield f"data: {json.dumps(event_payload)}\n\n"

        # Final complete payload event
        completed_run = await _execute_pipeline(ticker, horizon, depth, gateway, analysis_id)
        ANALYSIS_CACHE[analysis_id] = {"analysisId": analysis_id, "run": completed_run}
        yield f"data: {json.dumps({'analysisId': analysis_id, 'status': 'completed', 'run': completed_run})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def _execute_pipeline(ticker: str, horizon: str, depth: str, gateway: str, analysis_id: str) -> Dict[str, Any]:
    """Internal multi-agent pipeline execution logic."""
    market = await MarketService.get_stock_data(ticker)
    technical = await TechnicalService.calculate_indicators(ticker)
    fundamental = await FundamentalService.get_fundamentals(ticker)
    news = await NewsService.get_news_sentiment(ticker)
    historical = await HistoricalService.find_analogues(ticker)

    features = FeatureBuilder.build_feature_vector(
        market, technical, fundamental, news, historical, datetime.utcnow()
    )

    prediction = await MLEngine.predict(ticker, horizon, features)
    critic = await CriticService.validate(market, technical, fundamental, news, prediction)
    summary = await ModelGateway.generate_synthesis(
        gateway, ticker, market, technical, fundamental, news, prediction, critic
    )

    return {
        "analysisId": analysis_id,
        "ticker": ticker.upper(),
        "horizon": horizon,
        "depth": depth,
        "status": "completed",
        "createdAt": datetime.utcnow().isoformat(),
        "completedAt": datetime.utcnow().isoformat(),
        "prediction": prediction,
        "critic": critic,
        "summary": summary,
    }
