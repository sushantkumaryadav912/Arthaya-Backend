from sqlalchemy import Column, String, Text, DateTime, JSON, Float
from datetime import datetime
from app.database import Base

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(50), primary_key=True, index=True)
    analysis_id = Column(String(50), nullable=True)
    ticker = Column(String(20), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    content_markdown = Column(Text, nullable=False)
    
    overall_signal = Column(String(20), nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(String(25), nullable=False)
    model_name = Column(String(50), nullable=False)
    
    sections = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
