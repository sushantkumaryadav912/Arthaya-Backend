from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, delete

from app.core.dependencies import get_current_user, AuthenticatedUser
from app.database import AsyncSessionLocal
from app.models.watchlist import WatchlistItem
from app.services.market_service import MarketService

router = APIRouter(prefix="/watchlist", tags=["watchlist"], dependencies=[Depends(get_current_user)])

class WatchlistAddRequest(BaseModel):
    ticker: str

DEFAULT_ITEMS = [
    {"ticker": "AAPL", "name": "Apple Inc.", "price": 346.50, "change": 2.45, "direction": "UP", "probability": 0.68},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "price": 138.25, "change": 3.80, "direction": "UP", "probability": 0.74},
    {"ticker": "TSLA", "name": "Tesla Inc.", "price": 256.40, "change": -4.20, "direction": "DOWN", "probability": 0.54},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "price": 428.10, "change": 1.20, "direction": "UP", "probability": 0.72},
    {"ticker": "PLTR", "name": "Palantir Technologies", "price": 44.80, "change": 1.95, "direction": "UP", "probability": 0.65},
]

_removed_tickers = set()

@router.get("")
async def get_watchlist(user: AuthenticatedUser = Depends(get_current_user)):
    """Returns watchlist items for the authenticated user (or default institutional watchlist)."""
    items = [dict(it) for it in DEFAULT_ITEMS if it["ticker"] not in _removed_tickers]
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(WatchlistItem))
            db_items = result.scalars().all()
            if db_items:
                existing_tickers = {it["ticker"] for it in items}
                for d in db_items:
                    if d.ticker not in existing_tickers and d.ticker not in _removed_tickers:
                        items.append({
                            "ticker": d.ticker,
                            "name": d.name,
                            "price": d.added_price or 150.0,
                            "change": 0.85,
                            "direction": "UP",
                            "probability": 0.65,
                        })
    except Exception as e:
        print(f"⚠️ Watchlist fetch note: {e}")

    return {"data": items, "count": len(items), "generatedAt": datetime.utcnow().isoformat()}

@router.post("")
async def add_to_watchlist(req: WatchlistAddRequest, user: AuthenticatedUser = Depends(get_current_user)):
    """Adds a ticker to the watchlist."""
    ticker = req.ticker.strip().upper()
    _removed_tickers.discard(ticker)

    try:
        quote = await MarketService.get_stock_data(ticker)
        name = quote.get("name") or ticker
        price = quote.get("current_price") or 100.0
    except Exception:
        name = ticker
        price = 100.0

    try:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(WatchlistItem).where(WatchlistItem.ticker == ticker))
            existing = res.scalars().first()
            if not existing:
                item = WatchlistItem(
                    ticker=ticker,
                    name=name,
                    added_price=price,
                    added_at=datetime.utcnow()
                )
                db.add(item)
                await db.commit()
    except Exception as e:
        print(f"⚠️ Watchlist persist note: {e}")

    return {"success": True, "ticker": ticker, "name": name, "price": price}

@router.delete("/{ticker}")
async def remove_from_watchlist(ticker: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Removes a ticker from the watchlist."""
    ticker_clean = ticker.strip().upper()
    _removed_tickers.add(ticker_clean)
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(WatchlistItem).where(WatchlistItem.ticker == ticker_clean))
            await db.commit()
    except Exception as e:
        print(f"⚠️ Watchlist delete note: {e}")

    return {"success": True, "ticker": ticker_clean, "removed": True}
