from fastapi import APIRouter
from app.services.ml_engine import MLEngine
from app.services.feature_builder import FeatureBuilder

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.get("/{ticker}")
async def get_prediction(ticker: str, horizon: str = "5D"):
    features = {
        "rsi_14": 62.4,
        "news_sentiment": 0.68,
        "historical_up_frequency": 0.75,
        "momentum_20d": 0.074
    }
    prediction = await MLEngine.predict(ticker, horizon, features)
    return {"data": prediction, "demo": True, "generatedAt": "2026-10-08T09:00:00Z"}
