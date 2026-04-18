"""
Unified Advisor - Connects Stock + Jyotish
"""

import json
from datetime import datetime
from engines.mamba_engine import get_creative_llm, get_balanced_llm
from engines.ephemeris_engine import EphemerisEngine
from agents.stock_data_agent import StockDataAgent
from agents.analysis_chain import StockAnalysisChain
from agents.sentiment_agent import SentimentAgent
from agents.jyotish_agent import JyotishAgent
from config.settings import COMBINED_DISCLAIMER


class UnifiedAdvisor:
    """Combines Stock Analysis + Jyotish Predictions"""

    def __init__(self):
        self.stock_agent = StockAnalysisChain()
        self.sentiment_agent = SentimentAgent()
        self.jyotish_agent = JyotishAgent()
        self.ephemeris = EphemerisEngine()
        self.llm = get_creative_llm()

    def complete_stock_analysis(
        self, ticker, company_name, listing_date=None
    ):
        """Run ALL analyses and combine"""

        results = {
            "ticker": ticker,
            "company": company_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "analyses": {}
        }

        # 1. Fundamental
        try:
            results["analyses"]["fundamental"] = \
                self.stock_agent.analyze_stock(ticker)
        except Exception as e:
            results["analyses"]["fundamental"] = "Error: " + str(e)

        # 2. Sentiment
        try:
            results["analyses"]["sentiment"] = \
                self.sentiment_agent.analyze_sentiment(
                    ticker, company_name
                )
        except Exception as e:
            results["analyses"]["sentiment"] = "Error: " + str(e)

        # 3. Planetary
        try:
            report = self.ephemeris.get_market_report()
            results["analyses"]["planetary"] = report
        except Exception as e:
            results["analyses"]["planetary"] = {"error": str(e)}

        # 4. Jyotish Market
        try:
            results["analyses"]["jyotish"] = \
                self.jyotish_agent.predict_market_trend()
        except Exception as e:
            results["analyses"]["jyotish"] = "Error: " + str(e)

        # 5. Stock Kundali
        if listing_date:
            try:
                results["analyses"]["kundali"] = \
                    self.jyotish_agent.analyze_stock_astrology(
                        ticker, listing_date
                    )
            except Exception as e:
                results["analyses"]["kundali"] = "Error: " + str(e)

        # 6. Combined Verdict
        results["combined_verdict"] = self._combine(results)
        results["disclaimer"] = COMBINED_DISCLAIMER

        return results

    def _combine(self, results):
        """Synthesize all analyses"""

        fundamental = str(
            results["analyses"].get("fundamental", "N/A")
        )
        sentiment = str(
            results["analyses"].get("sentiment", "N/A")
        )
        planetary = results["analyses"].get("planetary", {})
        jyotish = str(
            results["analyses"].get("jyotish", "N/A")
        )
        kundali = str(
            results["analyses"].get("kundali", "N/A")
        )

        if isinstance(planetary, dict):
            mood = planetary.get("market_mood", "Unknown")
            planetary_text = "Market Mood: " + mood
        else:
            planetary_text = str(planetary)

        prompt = """You are the Ultimate Stock Advisor combining 
modern finance with Vedic Jyotish wisdom.

STOCK: """ + results["company"] + " (" + results["ticker"] + ")" + """
DATE: """ + results["timestamp"] + """

## FUNDAMENTAL ANALYSIS:
""" + fundamental[:3000] + """

## SENTIMENT:
""" + sentiment[:2000] + """

## PLANETARY STATE:
""" + planetary_text + """

## JYOTISH PREDICTION:
""" + jyotish[:2000] + """

## STOCK KUNDALI:
""" + kundali[:2000] + """

## PROVIDE UNIFIED RECOMMENDATION:

### SCORES:
- Fundamental: _/10
- Sentiment: _/10
- Jyotish: _/10
- OVERALL: _/10

### WHERE ALL THREE AGREE:
(High confidence signals)

### WHERE THEY DISAGREE:
(Explain conflicts)

### UNIFIED VERDICT:
- Action: BUY / HOLD / SELL / WAIT
- Confidence: HIGH / MEDIUM / LOW
- Risk: LOW / MODERATE / HIGH

### TIMING (Short/Medium/Long):
Entry, Target, Stop Loss for each.

### JYOTISH TIMING:
Best dates to act.

Disclaimer: Combines analysis with astrology (speculative). 
Not financial advice.
"""
        return self.llm(prompt)

    def get_dashboard_data(self):
        """Quick dashboard data"""
        try:
            report = self.ephemeris.get_market_report()
        except Exception:
            report = {"market_mood": "UNKNOWN"}

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "planetary_report": report,
            "disclaimer": COMBINED_DISCLAIMER
        }

    def jyotish_sector_rotation(self):
        """Sector rotation based on planets"""
        positions = self.ephemeris.get_planetary_positions()
        yogas = self.ephemeris.detect_yogas(positions)

        prompt = """You are a Sector Rotation Strategist using 
Vedic Astrology.

Planetary Positions:
""" + json.dumps(positions, indent=2, default=str) + """

Active Yogas:
""" + json.dumps(yogas, indent=2, default=str) + """

## SECTOR ROTATION:

### OVERWEIGHT (Strong planetary support):
List sectors with reasons and top picks.

### UNDERWEIGHT (Weak planets):
List sectors to reduce.

### NEUTRAL:
List with reasoning.

### MODEL PORTFOLIO:
Sector allocation percentages based on current planets.

Disclaimer: Based on Vedic Astrology. Speculative.
"""
        return self.llm(prompt)


if __name__ == "__main__":
    print("Testing Unified Advisor...")
    advisor = UnifiedAdvisor()
    dashboard = advisor.get_dashboard_data()
    print("Timestamp: " + dashboard["timestamp"])
    mood = dashboard["planetary_report"].get("market_mood", "?")
    print("Market Mood: " + mood)
    print("Unified Advisor loaded OK")