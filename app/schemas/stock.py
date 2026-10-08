from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StockBase(BaseModel):
    ticker: str
    name: str
    exchange: str = "NASDAQ"
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None

class StockResponse(StockBase):
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TechnicalIndicators(BaseModel):
    rsi_14: float
    sma_20: float
    sma_50: float
    sma_200: float
    macd: float
    macd_signal: float
    atr_14: float
    bollinger_upper: float
    bollinger_lower: float
    momentum_20d: float
    interpretation: str

class FundamentalData(BaseModel):
    revenue: float
    net_income: float
    eps: float
    pe_ratio: float
    pb_ratio: float
    ps_ratio: float
    roe: float
    roa: float
    debt_to_equity: float
    free_cash_flow: float
    revenue_growth_yoy: float
    eps_growth_yoy: float
    interpretation: str
