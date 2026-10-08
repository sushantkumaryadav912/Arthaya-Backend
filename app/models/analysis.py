from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(50), primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    horizon = Column(String(10), nullable=False, default="5D")
    depth = Column(String(20), nullable=False, default="standard")
    status = Column(String(20), nullable=False, default="queued") # queued, running, completed, failed
    gateway_provider = Column(String(50), nullable=False, default="claude")
    n8n_execution_id = Column(String(100), nullable=True)
    
    # JSON payload fields for structured output
    critic_validation = Column(JSON, nullable=True)
    ai_summary = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("AgentStepLog", back_populates="analysis", cascade="all, delete-orphan")

class AgentStepLog(Base):
    __tablename__ = "agent_step_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(50), ForeignKey("analysis_runs.id"), nullable=False)
    agent_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False) # idle, running, completed, error
    message = Column(String(500), nullable=True)
    progress = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisRun", back_populates="steps")
