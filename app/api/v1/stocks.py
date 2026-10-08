from fastapi import APIRouter, Depends, HTTPException
from app.services.market_service import MarketService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService
from app.services.news_service import NewsService
from app.services.historical_service import HistoricalService

router = APIRouter(prefix="/stocks", tags=["stocks"])

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
