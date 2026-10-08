from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ModelVote(BaseModel):
    model: str
    direction: str
    probability: float

class PredictionResponse(BaseModel):
    id: str
    ticker: str
    horizon: str
    direction: str
    probability: float
    model: str
    model_version: str
    predicted_at: datetime
    data_cutoff: datetime
    breakdown: Optional[List[ModelVote]] = None
    features_used: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True

class ModelPerformanceSchema(BaseModel):
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    log_loss: Optional[float] = None
    brier: Optional[float] = None
