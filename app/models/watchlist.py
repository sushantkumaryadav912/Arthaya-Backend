from sqlalchemy import Column, String, Float, DateTime, Integer
from datetime import datetime
from app.database import Base

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    added_price = Column(Float, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
