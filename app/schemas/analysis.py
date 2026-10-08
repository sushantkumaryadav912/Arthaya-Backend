from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    ticker: str
    horizon: str = "5D"
    depth: str = "standard"
    gateway_provider: str = "claude"

class AgentStepSchema(BaseModel):
    agent_id: str
    status: str # idle, running, completed, error
    message: Optional[str] = None
    progress: int = 0
    timestamp: Optional[datetime] = None

class AnalysisEventSchema(BaseModel):
    analysis_id: str
    agent: str
    status: str
    message: str
    progress: Optional[int] = None
    timestamp: str
    clock: Optional[str] = None

class CriticValidationSchema(BaseModel):
    data_quality: Optional[float] = None
    model_quality: Optional[float] = None
    source_quality: Optional[float] = None
    signal_agreement: Optional[float] = None
    model_calibration: Optional[float] = None
    potential_leakage: Optional[str] = "none"
    missing_data: List[str] = []
    stale_data: List[str] = []
    notes: List[str] = []

class AIResearchSummarySchema(BaseModel):
    overall_signal: str # UP, DOWN, NEUTRAL
    probability: float
    horizon_days: int
    confidence: str # Low, Moderate, High
    market_context: str
    technical_view: str
    fundamental_view: str
    news_view: str
    historical_context: str
    model_prediction: str
    risk_factors: List[str] = []
    conflicting_signals: List[str] = []
    data_quality: str
    agreement: Dict[str, str] = {}

class AnalysisRunResponse(BaseModel):
    analysis_id: str
    ticker: str
    horizon: str
    depth: str
    status: str
    gateway_provider: str
    steps: List[AgentStepSchema] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
    critic: Optional[CriticValidationSchema] = None
    summary: Optional[AIResearchSummarySchema] = None

    class Config:
        from_attributes = True
