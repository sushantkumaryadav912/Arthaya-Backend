from fastapi import APIRouter

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

@router.get("")
async def get_watchlist():
    return {
        "data": [
            {"ticker": "AAPL", "name": "Apple Inc.", "price": 224.50, "change": 1.25, "direction": "UP", "probability": 0.68},
            {"ticker": "NVDA", "name": "NVIDIA Corp.", "price": 128.80, "change": -0.40, "direction": "UP", "probability": 0.61},
            {"ticker": "TSLA", "name": "Tesla Inc.", "price": 242.10, "change": 2.10, "direction": "DOWN", "probability": 0.54},
            {"ticker": "MSFT", "name": "Microsoft Corp.", "price": 418.30, "change": 0.85, "direction": "UP", "probability": 0.72},
        ],
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }
