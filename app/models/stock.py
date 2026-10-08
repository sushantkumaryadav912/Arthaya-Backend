from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime
from app.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=False, default="NASDAQ")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    current_price = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
