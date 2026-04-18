"""
Stock Analysis Chain - No LLMChain dependency
"""

import json
from engines.mamba_engine import get_balanced_llm
from agents.stock_data_agent import StockDataAgent


class StockAnalysisChain:
    """Stock analysis using direct Mamba2 calls"""

    def __init__(self):
        self.llm = get_balanced_llm()
        self.data_agent = StockDataAgent()

    def analyze_stock(self, ticker):
        """Complete stock analysis"""
        info = self.data_agent.get_stock_info(ticker)
        financials = self.data_agent.get_financials(ticker)

        prompt = """You are an expert stock analyst.

## Stock Data:
""" + json.dumps(info, indent=2) + """

## Financial Statements:
""" + str(financials) + """

## Provide:

### 1. FUNDAMENTAL ANALYSIS
- Revenue and profit trends
- Valuation assessment (PE, PB ratios)
- Debt health
- Cash flow quality
- Management efficiency (ROE)

### 2. STRENGTHS (Top 5)

### 3. RISKS (Top 5)

### 4. INVESTMENT VERDICT
- Short term (1-3 months)
- Medium term (6-12 months)
- Long term (2-5 years)
- Action: BUY / HOLD / WAIT / AVOID

### 5. FAIR VALUE ESTIMATE

Disclaimer: AI-generated. Not financial advice.
"""
        return self.llm(prompt)

    def find_best_stocks(self, investment_style):
        """Find stocks based on style"""

        criteria_map = {
            "value": {
                "max_pe": 15,
                "min_roe": 0.12,
                "min_market_cap": 5000000000
            },
            "growth": {
                "min_roe": 0.20,
                "min_market_cap": 10000000000
            },
            "dividend": {
                "min_dividend": 0.03,
                "min_market_cap": 10000000000
            },
            "balanced": {
                "max_pe": 25,
                "min_roe": 0.15,
                "min_market_cap": 10000000000
            }
        }

        criteria = criteria_map.get(
            investment_style, criteria_map["balanced"]
        )
        screened = self.data_agent.screen_stocks(criteria)

        prompt = """You are an expert investment advisor.

Investment Style: """ + investment_style + """

Screened Stocks:
""" + json.dumps(screened, indent=2) + """

## Tasks:
1. Rank stocks BEST to WORST for this style
2. For TOP 5, explain WHY
3. Suggest portfolio allocation percentages
4. Identify stocks to AVOID
5. Suggest entry prices

Disclaimer: Educational only. Not financial advice.
"""
        return self.llm(prompt)

    def analyze_mutual_fund(self, fund_name):
        """Analyze mutual fund"""

        prompt = """You are a mutual fund expert.

Fund: """ + fund_name + """

Provide:
1. Fund category and style
2. Typical holdings
3. Risk assessment (1-10)
4. Best suited investor profile
5. SIP vs Lumpsum recommendation
6. Comparison with peers
7. Red flags

Disclaimer: Educational only. Not financial advice.
"""
        return self.llm(prompt)


if __name__ == "__main__":
    chain = StockAnalysisChain()
    print("Analysis Chain loaded OK")