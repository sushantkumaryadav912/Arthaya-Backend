from fastapi import APIRouter, HTTPException, Depends
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
from app.core.dependencies import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisStartRequest(BaseModel):
    ticker: str
    horizon: str = "5D"
    depth: str = "standard"
    gateway_provider: str = "claude"

# In-memory analysis cache for real-time streaming
ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}

@router.post("")
async def start_analysis(req: AnalysisStartRequest, user: AuthenticatedUser = Depends(get_current_user)):
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

class N8NWebhookPayload(BaseModel):
    status: Optional[str] = "completed"
    agent: Optional[str] = None
    message: Optional[str] = None
    progress: Optional[int] = None
    data: Optional[Dict[str, Any]] = None

@router.post("/{analysis_id}/webhook")
async def n8n_webhook_callback(analysis_id: str, payload: Dict[str, Any]):
    """Receives asynchronous workflow completion or step updates from n8n Orchestrator."""
    if analysis_id not in ANALYSIS_CACHE:
        ANALYSIS_CACHE[analysis_id] = {
            "analysisId": analysis_id,
            "status": payload.get("status", "running"),
            "updatedAt": datetime.utcnow().isoformat(),
        }
    
    # Update cache with payload data
    cached = ANALYSIS_CACHE[analysis_id]
    cached["status"] = payload.get("status", cached.get("status", "completed"))
    cached["updatedAt"] = datetime.utcnow().isoformat()
    if "data" in payload or "run" in payload:
        cached["run"] = payload.get("data") or payload.get("run")
    if "agent" in payload:
        cached.setdefault("agent_updates", []).append(payload)

    return {"received": True, "analysis_id": analysis_id, "status": cached["status"]}

@router.get("/{id_or_ticker}")
async def get_analysis_result(
    id_or_ticker: str,
    horizon: str = "5D",
    depth: str = "standard",
    gateway: str = "claude"
):
    """Retrieves cached analysis run or generates real multi-agent analysis for given ticker/run ID."""
    if id_or_ticker in ANALYSIS_CACHE and "run" in ANALYSIS_CACHE[id_or_ticker]:
        return {"data": ANALYSIS_CACHE[id_or_ticker]["run"], "demo": False, "generatedAt": datetime.utcnow().isoformat()}

    ticker = id_or_ticker.upper() if len(id_or_ticker) <= 6 and not id_or_ticker.startswith("ana_") else "AAPL"
    analysis_id = id_or_ticker if id_or_ticker.startswith("ana_") else f"ana_{uuid.uuid4().hex[:10]}"

    run_data = await _execute_pipeline(ticker, horizon, depth, gateway, analysis_id)
    return {"data": run_data, "demo": False, "generatedAt": datetime.utcnow().isoformat()}

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

class CriticValidateRequest(BaseModel):
    analysis_id: str
    ticker: str

class SynthesisRequest(BaseModel):
    analysis_id: str
    ticker: str
    gateway_provider: str = "claude"

@router.post("/critic-validate")
async def critic_validate_endpoint(req: CriticValidateRequest):
    market = await MarketService.get_stock_data(req.ticker)
    technical = await TechnicalService.calculate_indicators(req.ticker)
    fundamental = await FundamentalService.get_fundamentals(req.ticker)
    news = await NewsService.get_news_sentiment(req.ticker)
    features = FeatureBuilder.build_feature_vector(market, technical, fundamental, news, {}, datetime.utcnow())
    prediction = await MLEngine.predict(req.ticker, "5D", features)
    
    critic_result = await CriticService.validate(market, technical, fundamental, news, prediction)
    return {"data": critic_result, "status": "completed"}

@router.post("/synthesis")
async def synthesis_endpoint(req: SynthesisRequest):
    market = await MarketService.get_stock_data(req.ticker)
    technical = await TechnicalService.calculate_indicators(req.ticker)
    fundamental = await FundamentalService.get_fundamentals(req.ticker)
    news = await NewsService.get_news_sentiment(req.ticker)
    features = FeatureBuilder.build_feature_vector(market, technical, fundamental, news, {}, datetime.utcnow())
    prediction = await MLEngine.predict(req.ticker, "5D", features)
    critic = await CriticService.validate(market, technical, fundamental, news, prediction)
    
    summary = await ModelGateway.generate_synthesis(
        req.gateway_provider, req.ticker, market, technical, fundamental, news, prediction, critic
    )
    return {"data": summary, "status": "completed"}

from app.database import AsyncSessionLocal
from app.models.analysis import AnalysisRun, AgentStepLog
from app.models.prediction import PredictionRecord
from app.models.report import ResearchReport

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

    # Persist analysis run, prediction, and report to SQLite database
    try:
        async with AsyncSessionLocal() as db:
            analysis_record = AnalysisRun(
                id=analysis_id,
                ticker=ticker.upper(),
                horizon=horizon,
                depth=depth,
                status="completed",
                gateway_provider=gateway,
                critic_validation=critic,
                ai_summary=summary,
                completed_at=datetime.utcnow()
            )
            db.add(analysis_record)

            pred_record = PredictionRecord(
                id=f"pred_{uuid.uuid4().hex[:10]}",
                analysis_id=analysis_id,
                ticker=ticker.upper(),
                horizon=horizon,
                direction=prediction.get("direction", "NEUTRAL"),
                probability=prediction.get("probability", 0.5),
                model=prediction.get("model", "XGBoost"),
                model_version=prediction.get("model_version", "xgb_1.3"),
                breakdown=prediction.get("breakdown", []),
                features_used=prediction.get("features_used", {})
            )
            db.add(pred_record)

            report_record = ResearchReport(
                id=f"rep_{uuid.uuid4().hex[:10]}",
                analysis_id=analysis_id,
                ticker=ticker.upper(),
                company_name=market.get("name", ticker),
                title=f"{ticker.upper()} Multi-Agent Financial Research Report",
                summary=summary.get("market_context", ""),
                content_markdown=f"### Technical View\n{summary.get('technical_view', '')}\n\n### Fundamental View\n{summary.get('fundamental_view', '')}",
                overall_signal=summary.get("overall_signal", "NEUTRAL"),
                probability=float(summary.get("probability", 0.5)),
                confidence=summary.get("confidence", "Medium"),
                model_name=gateway
            )
            db.add(report_record)
            await db.commit()
            print(f"💾 Persisted Analysis {analysis_id} into SQLite database!")
    except Exception as db_err:
        print(f"⚠️ Database persistence notice: {db_err}")

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

