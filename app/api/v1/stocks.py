from fastapi import APIRouter, Depends, HTTPException
from app.services.market_service import MarketService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService
from app.services.news_service import NewsService
from app.services.historical_service import HistoricalService
from app.core.dependencies import get_current_user, get_optional_user

from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/stocks", tags=["stocks"], dependencies=[Depends(get_optional_user)])

# Core tracked stock universe
UNIVERSE = [
    {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "price": 346.50, "change": 2.45, "changePercent": 0.72},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology", "price": 138.25, "change": 3.80, "changePercent": 2.83},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "price": 428.10, "change": 1.20, "changePercent": 0.28},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary", "price": 256.40, "change": -4.20, "changePercent": -1.61},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "price": 182.75, "change": 1.65, "changePercent": 0.91},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary", "price": 194.20, "change": 0.85, "changePercent": 0.44},
    {"ticker": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "price": 582.30, "change": 7.40, "changePercent": 1.29},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "exchange": "NASDAQ", "sector": "Technology", "price": 164.50, "change": 2.10, "changePercent": 1.29},
    {"ticker": "PLTR", "name": "Palantir Technologies", "exchange": "NYSE", "sector": "Technology", "price": 44.80, "change": 1.95, "changePercent": 4.55},
]

@router.get("")
async def list_stocks(q: Optional[str] = None):
    """Lists tracked equity universe or searches by query string."""
    items = UNIVERSE
    if q and q.strip():
        query = q.strip().upper()
        items = [s for s in UNIVERSE if query in s["ticker"].upper() or query in s["name"].upper()]
    return {"data": items, "demo": False, "count": len(items)}

@router.get("/{ticker}")
async def get_stock_detail(ticker: str):
    data = await MarketService.get_stock_data(ticker)
    return {"data": data, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}

@router.get("/{ticker}/technical")
async def get_stock_technical(ticker: str):
    data = await TechnicalService.calculate_indicators(ticker)
    return {"data": data, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}

@router.get("/{ticker}/fundamentals")
async def get_stock_fundamentals(ticker: str):
    data = await FundamentalService.get_fundamentals(ticker)
    return {"data": data, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}

@router.get("/{ticker}/news")
async def get_stock_news(ticker: str):
    data = await NewsService.get_news_sentiment(ticker)
    return {"data": data, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}

@router.get("/{ticker}/historical")
async def get_stock_historical(ticker: str):
    data = await HistoricalService.find_analogues(ticker)
    return {"data": data, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}
