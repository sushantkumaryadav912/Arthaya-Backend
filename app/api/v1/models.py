from fastapi import APIRouter

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/performance")
async def get_model_performance():
    return {
        "data": {
            "models": [
                {
                    "model": "XGBoost",
                    "classification": {"accuracy": 0.684, "precision": 0.672, "recall": 0.710, "f1": 0.690, "rocAuc": 0.732, "logLoss": 0.582, "brier": 0.198},
                    "regression": {"mae": 0.0142, "rmse": 0.0218},
                },
                {
                    "model": "Random Forest",
                    "classification": {"accuracy": 0.651, "precision": 0.640, "recall": 0.680, "f1": 0.659, "rocAuc": 0.698, "logLoss": 0.612, "brier": 0.214},
                    "regression": {"mae": 0.0165, "rmse": 0.0245},
                },
                {
                    "model": "Logistic Regression",
                    "classification": {"accuracy": 0.612, "precision": 0.605, "recall": 0.630, "f1": 0.617, "rocAuc": 0.652, "logLoss": 0.648, "brier": 0.231},
                    "regression": {"mae": 0.0189, "rmse": 0.0281},
                },
            ],
            "walkForward": [
                {"period": "2024 Q1", "trainWindow": "2020-2023", "testWindow": "2024 Q1", "accuracy": 0.665, "rocAuc": 0.710},
                {"period": "2024 Q2", "trainWindow": "2020-2024 Q1", "testWindow": "2024 Q2", "accuracy": 0.692, "rocAuc": 0.741},
                {"period": "2024 Q3", "trainWindow": "2020-2024 Q2", "testWindow": "2024 Q3", "accuracy": 0.678, "rocAuc": 0.725},
                {"period": "2024 Q4", "trainWindow": "2020-2024 Q3", "testWindow": "2024 Q4", "accuracy": 0.701, "rocAuc": 0.753},
            ],
            "baselines": [
                {"name": "Naive Baseline", "accuracy": 0.521, "rocAuc": 0.500, "note": "Always predicts historical majority class"},
                {"name": "Technical-only", "accuracy": 0.598, "rocAuc": 0.632, "note": "RSI + MACD + Moving Averages only"},
                {"name": "Fundamental-only", "accuracy": 0.564, "rocAuc": 0.591, "note": "P/E + Revenue Growth + ROE only"},
                {"name": "News-only", "accuracy": 0.582, "rocAuc": 0.615, "note": "NLP sentiment score only"},
                {"name": "Multi-source", "accuracy": 0.684, "rocAuc": 0.732, "note": "Full Arthaya multi-agent feature engine"},
            ],
            "evaluatedAt": "2026-10-08T00:00:00Z",
        },
        "demo": True,
        "generatedAt": "2026-10-08T09:00:00Z"
    }
