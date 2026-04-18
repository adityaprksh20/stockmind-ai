"""
Stock Data Agent - Fetches real-time market data
"""

import yfinance as yf
import pandas as pd
from config.settings import NIFTY50_TICKERS, US_TICKERS


class StockDataAgent:
    """Fetches and processes stock/fund data"""

    def get_stock_info(self, ticker):
        """Get comprehensive stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "market_cap_formatted": self._format_market_cap(
                    info.get("marketCap", 0)
                ),
                "pe_ratio": round(
                    info.get("trailingPE", 0) or 0, 2
                ),
                "forward_pe": round(
                    info.get("forwardPE", 0) or 0, 2
                ),
                "pb_ratio": round(
                    info.get("priceToBook", 0) or 0, 2
                ),
                "dividend_yield": round(
                    (info.get("dividendYield", 0) or 0) * 100, 2
                ),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "current_price": (
                    info.get("currentPrice", 0)
                    or info.get("regularMarketPrice", 0)
                ),
                "debt_to_equity": round(
                    info.get("debtToEquity", 0) or 0, 2
                ),
                "roe": round(
                    info.get("returnOnEquity", 0) or 0, 4
                ),
                "revenue_growth": round(
                    info.get("revenueGrowth", 0) or 0, 4
                ),
                "profit_margins": round(
                    info.get("profitMargins", 0) or 0, 4
                ),
                "free_cashflow": info.get("freeCashflow", 0),
                "recommendation": info.get(
                    "recommendationKey", "N/A"
                ),
                "target_price": info.get("targetMeanPrice", 0),
            }
        except Exception as e:
            return {
                "ticker": ticker,
                "name": "Error fetching data",
                "error": str(e)
            }

    def _format_market_cap(self, market_cap):
        """Format market cap to readable string"""
        if not market_cap:
            return "N/A"
        if market_cap >= 1e12:
            return f"₹{market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"₹{market_cap/1e9:.2f}B"
        elif market_cap >= 1e7:
            return f"₹{market_cap/1e7:.2f}Cr"
        elif market_cap >= 1e6:
            return f"₹{market_cap/1e6:.2f}M"
        else:
            return f"₹{market_cap}"

    def get_historical_data(self, ticker, period="1y"):
        """Get historical price data"""
        try:
            stock = yf.Ticker(ticker)
            return stock.history(period=period)
        except Exception as e:
            return pd.DataFrame()

    def get_financials(self, ticker):
        """Get financial statements"""
        try:
            stock = yf.Ticker(ticker)
            return {
                "income_statement": stock.financials.to_string()
                if stock.financials is not None
                else "Not available",
                "balance_sheet": stock.balance_sheet.to_string()
                if stock.balance_sheet is not None
                else "Not available",
                "cashflow": stock.cashflow.to_string()
                if stock.cashflow is not None
                else "Not available",
            }
        except Exception as e:
            return {
                "income_statement": f"Error: {str(e)}",
                "balance_sheet": f"Error: {str(e)}",
                "cashflow": f"Error: {str(e)}",
            }

    def screen_stocks(self, criteria):
        """
        Screen stocks based on criteria
        Example:
        {
            "min_market_cap": 10000000000,
            "max_pe": 25,
            "min_roe": 0.15,
            "min_dividend": 0.02
        }
        """
        results = []
        tickers = NIFTY50_TICKERS + US_TICKERS

        for ticker in tickers:
            try:
                info = self.get_stock_info(ticker)

                if "error" in info:
                    continue

                passes = True

                if (criteria.get("min_market_cap") and
                        info["market_cap"] < criteria["min_market_cap"]):
                    passes = False

                if (criteria.get("max_pe") and
                        info["pe_ratio"] > 0 and
                        info["pe_ratio"] > criteria["max_pe"]):
                    passes = False

                if (criteria.get("min_roe") and
                        info["roe"] and
                        info["roe"] < criteria["min_roe"]):
                    passes = False

                if (criteria.get("min_dividend") and
                        info["dividend_yield"] <
                        criteria["min_dividend"] * 100):
                    passes = False

                if passes:
                    results.append(info)

            except Exception:
                continue

        return results


# Quick test
if __name__ == "__main__":
    agent = StockDataAgent()
    info = agent.get_stock_info("RELIANCE.NS")
    print(f"Name: {info.get('name')}")
    print(f"Price: {info.get('current_price')}")
    print(f"PE: {info.get('pe_ratio')}")