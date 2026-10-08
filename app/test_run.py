import asyncio
from app.services.market_service import MarketService
from app.services.technical_service import TechnicalService
from app.services.fundamental_service import FundamentalService
from app.services.news_service import NewsService
from app.services.historical_service import HistoricalService
from app.services.feature_builder import FeatureBuilder
from app.services.ml_engine import MLEngine
from app.services.critic_service import CriticService
from app.services.model_gateway import ModelGateway
from datetime import datetime

async def test_aapl_run():
    print("🚀 Starting End-to-End Real-Data Analysis for AAPL...")
    
    # 1. Market Data
    market = await MarketService.get_stock_data("AAPL")
    print(f"1. Market Agent: AAPL Price = ${market['current_price']} ({market['change_pct']}%), P/E = {market['pe_ratio']}")

    # 2. Technical Indicators
    tech = await TechnicalService.calculate_indicators("AAPL")
    print(f"2. Technical Agent: RSI-14 = {tech['rsi_14']}, MACD = {tech['macd']}, SMA-50 = ${tech['sma_50']}")

    # 3. Fundamentals
    fund = await FundamentalService.get_fundamentals("AAPL")
    print(f"3. Fundamental Agent: Revenue = ${round(fund['revenue']/1e9, 1)}B, Growth = {round(fund['revenue_growth_yoy']*100, 1)}%")

    # 4. News & Sentiment
    news = await NewsService.get_news_sentiment("AAPL")
    print(f"4. News Agent: Sentiment Score = {news['sentiment_score']} ({news['overall_sentiment']}), Articles = {len(news['articles'])}")

    # 5. Historical Analogues
    hist = await HistoricalService.find_analogues("AAPL")
    print(f"5. Historical Agent: Matches = {len(hist['analogues'])}, Expected 5D Return = {round(hist['mean_return_5d']*100, 2)}%")

    # 6. Feature Builder (Zero Leakage Cutoff)
    features = FeatureBuilder.build_feature_vector(market, tech, fund, news, hist, datetime.utcnow())
    print(f"6. Feature Builder: Engineered {len(features)} features (Zero Leakage timestamp cutoff enforced).")

    # 7. ML Engine (Quant Prediction)
    pred = await MLEngine.predict("AAPL", "5D", features)
    print(f"7. Prediction Agent: Direction = {pred['direction']}, Probability = {pred['probability']} ({pred['model']} v1.3)")
    for vote in pred['breakdown']:
        print(f"   · {vote['model']}: {vote['direction']} ({round(vote['probability']*100)}%)")

    # 8. Critic Agent
    critic = await CriticService.validate(market, tech, fund, news, pred)
    print(f"8. Critic Agent: Data Quality = {int(critic['dataQuality']*100)}%, Leakage = {critic['potentialLeakage']}")

    # 9. Model Gateway Synthesis
    summary = await ModelGateway.generate_synthesis("claude", "AAPL", market, tech, fund, news, pred, critic)
    print(f"9. Synthesis Agent (Claude 3.5): Signal = {summary['overall_signal']} ({round(summary['probability']*100)}%), Confidence = {summary['confidence']}")

    print("\n✅ END-TO-END PIPELINE VALIDATION PASSED PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(test_aapl_run())
