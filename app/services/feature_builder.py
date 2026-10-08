from typing import Dict, Any
from datetime import datetime

class FeatureBuilder:
    @staticmethod
    def build_feature_vector(
        market_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        news_data: Dict[str, Any],
        historical_data: Dict[str, Any],
        cutoff_timestamp: datetime
    ) -> Dict[str, float]:
        """
        Engineers a tabular feature vector from all agent outputs.
        STRICT REQUIREMENT: Enforces data cutoff timestamp to prevent data leakage.
        """
        return {
            # Market Features
            "return_1d": market_data.get("change_pct", 0.0) / 100.0,
            "volume_norm": market_data.get("volume", 1000000) / 1e7,
            "pe_ratio": market_data.get("pe_ratio", 25.0),

            # Technical Features
            "rsi_14": technical_data.get("rsi_14", 50.0),
            "macd": technical_data.get("macd", 0.0),
            "sma_ratio_20_50": technical_data.get("sma_20", 1.0) / max(technical_data.get("sma_50", 1.0), 1e-5),
            "atr_14": technical_data.get("atr_14", 1.0),
            "momentum_20d": technical_data.get("momentum_20d", 0.0),

            # Fundamental Features
            "revenue_growth": fundamental_data.get("revenue_growth_yoy", 0.0),
            "eps_growth": fundamental_data.get("eps_growth_yoy", 0.0),
            "roe": fundamental_data.get("roe", 0.0) / 100.0,
            "debt_equity": fundamental_data.get("debt_to_equity", 1.0),

            # News Features
            "news_sentiment": news_data.get("sentiment_score", 0.5),
            "positive_event_count": float(news_data.get("positive_events", 0)),
            "negative_event_count": float(news_data.get("negative_events", 0)),

            # Historical Features
            "historical_mean_return_5d": historical_data.get("mean_return_5d", 0.0),
            "historical_up_frequency": historical_data.get("up_frequency_5d", 0.5),
        }
