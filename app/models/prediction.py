from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from datetime import datetime
from app.database import Base

class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(String(50), primary_key=True, index=True)
    analysis_id = Column(String(50), ForeignKey("analysis_runs.id"), nullable=True)
    ticker = Column(String(20), nullable=False, index=True)
    horizon = Column(String(10), nullable=False, default="5D")
    direction = Column(String(10), nullable=False) # UP, DOWN, NEUTRAL
    probability = Column(Float, nullable=False)
    model = Column(String(50), nullable=False, default="XGBoost")
    model_version = Column(String(20), nullable=False, default="xgb_1.3")
    
    # Model breakdowns (vote count per model)
    breakdown = Column(JSON, nullable=True)
    features_used = Column(JSON, nullable=True)
    
    predicted_at = Column(DateTime, default=datetime.utcnow)
    data_cutoff = Column(DateTime, default=datetime.utcnow)

class ModelPerformanceRecord(Base):
    __tablename__ = "model_performance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    log_loss = Column(Float, nullable=True)
    brier = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
