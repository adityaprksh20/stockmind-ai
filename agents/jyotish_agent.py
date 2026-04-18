"""
Jyotish Market Prediction Agent - No LLMChain dependency
"""

import json
from datetime import datetime
from engines.mamba_engine import get_creative_llm


class JyotishAgent:
    """Vedic Astrology market predictions"""

    def __init__(self):
        self.llm = get_creative_llm()

        self.planetary_significance = {
            "Sun": {
                "rules": "Government, gold, power",
                "impact": "PSU stocks, gold, govt policy"
            },
            "Moon": {
                "rules": "Sentiment, silver, emotions",
                "impact": "Volatility, FMCG, agriculture"
            },
            "Mars": {
                "rules": "Energy, real estate, military",
                "impact": "Defense, metals, energy"
            },
            "Mercury": {
                "rules": "IT, trade, banking",
                "impact": "IT sector, banking, telecom"
            },
            "Jupiter": {
                "rules": "Finance, law, expansion",
                "impact": "Banking, bull markets, gold"
            },
            "Venus": {
                "rules": "Luxury, entertainment, auto",
                "impact": "Auto, luxury, entertainment"
            },
            "Saturn": {
                "rules": "Oil, mining, discipline",
                "impact": "Oil/gas, infrastructure"
            },
            "Rahu": {
                "rules": "Technology, disruption",
                "impact": "Tech, crypto, volatility"
            },
            "Ketu": {
                "rules": "Pharma, spirituality",
                "impact": "Pharma, chemicals, crashes"
            }
        }

    def predict_market_trend(self, date=None):
        """Market prediction based on planets"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        pdata = json.dumps(self.planetary_significance, indent=2)

        prompt = """You are an expert Vedic Financial Astrologer.

Date: """ + date + """

Planetary Significance:
""" + pdata + """

## Provide:

### 1. PLANETARY TRANSIT ANALYSIS
Current transits affecting markets.

### 2. MARKET PREDICTION
- Next week direction
- Next month direction
- Key dates to watch

### 3. SECTOR ANALYSIS (Planet-Based)
For each: STRONG / NEUTRAL / WEAK
- Banking (Jupiter, Mercury)
- IT (Mercury, Rahu)
- Pharma (Ketu, Moon)
- Energy (Saturn, Mars)
- Auto (Venus, Mars)
- FMCG (Moon, Venus)

### 4. INVESTMENT TIMING
- Auspicious dates for buying
- Dates to avoid

### 5. RISK SCORE (1-10)

Disclaimer: Jyotish predictions are speculative. Not financial advice.
"""
        return self.llm(prompt)

    def analyze_stock_astrology(self, ticker, listing_date):
        """Stock kundali analysis"""

        pdata = json.dumps(self.planetary_significance, indent=2)

        prompt = """You are a Vedic Financial Astrologer.

Stock: """ + ticker + """
Listing Date: """ + listing_date + """

Planetary Data:
""" + pdata + """

## Stock Kundali Analysis:

### 1. LISTING CHART
Planetary positions at listing and chart strength.

### 2. CURRENT TRANSIT IMPACT
How transits affect this stock now.

### 3. PREDICTION
- Next 1 year outlook
- Key turning points

### 4. TIMING
- Best dates to BUY
- Best dates to SELL
- Dates to AVOID

Disclaimer: Speculative. Not financial advice.
"""
        return self.llm(prompt)

    def world_events_prediction(self):
        """Predict world events and market impact"""

        pdata = json.dumps(self.planetary_significance, indent=2)
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = """You are a Mundane Astrology (Medini Jyotish) expert.

Date: """ + today + """

Planetary Data:
""" + pdata + """

## PREDICTIONS:

### 1. GEOPOLITICAL
US-China, India economy, Middle East, market impact.

### 2. NATURAL EVENTS
Weather, agriculture, commodities.

### 3. GLOBAL MARKETS
US markets, Indian markets, gold, silver, oil.

### 4. POLICY
Interest rates (RBI, Fed), regulatory changes.

### 5. NEXT 3 MONTHS (Month by Month)
Key events, direction, sectors, risk level.

### 6. TOP 3 HIGH-CONVICTION PREDICTIONS

Disclaimer: Speculative. Not financial advice.
"""
        return self.llm(prompt)


if __name__ == "__main__":
    agent = JyotishAgent()
    print("Jyotish Agent loaded OK")