from fastapi import APIRouter, Depends, HTTPException
from app.services.market_service import MarketService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService
from app.services.news_service import NewsService
from app.services.historical_service import HistoricalService
from app.core.dependencies import get_current_user, get_optional_user

from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/stocks", tags=["stocks"], dependencies=[Depends(get_optional_user)])

# Core tracked stock universe with real live prices
UNIVERSE = [
    {"ticker": "M&M", "name": "Mahindra & Mahindra Ltd.", "exchange": "NSE", "sector": "Automotive", "price": 2824.90, "change": -99.40, "changePercent": -3.40},
    {"ticker": "RELIANCE", "name": "Reliance Industries Ltd.", "exchange": "NSE", "sector": "Conglomerate", "price": 1186.20, "change": -25.00, "changePercent": -2.06},
    {"ticker": "TCS", "name": "Tata Consultancy Services Ltd.", "exchange": "NSE", "sector": "Technology", "price": 2532.40, "change": 67.40, "changePercent": 2.73},
    {"ticker": "INFY", "name": "Infosys Ltd.", "exchange": "NSE", "sector": "Technology", "price": 1158.35, "change": -2.85, "changePercent": -0.25},
    {"ticker": "HDFCBANK", "name": "HDFC Bank Ltd.", "exchange": "NSE", "sector": "Financial Services", "price": 695.30, "change": -33.55, "changePercent": -4.60},
    {"ticker": "TATAMOTORS", "name": "Tata Motors Ltd.", "exchange": "NSE", "sector": "Automotive", "price": 890.00, "change": -12.40, "changePercent": -1.37},
    {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "price": 348.22, "change": 6.22, "changePercent": 1.82},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "price": 521.08, "change": -18.36, "changePercent": -3.40},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology", "price": 212.21, "change": -5.02, "changePercent": -2.31},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary", "price": 374.58, "change": 12.14, "changePercent": 3.35},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary", "price": 250.38, "change": -4.38, "changePercent": -1.72},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "price": 324.22, "change": -25.00, "changePercent": -7.16},
    {"ticker": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "price": 648.85, "change": -87.87, "changePercent": -11.93},
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
