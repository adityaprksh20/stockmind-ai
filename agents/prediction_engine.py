"""
Prediction Engine - Combines Market + Jyotish + Technical
into actionable BUY/SELL signals with confidence scores
"""

import json
from datetime import datetime
import yfinance as yf
import pandas as pd

from engines.mamba_engine import get_factual_llm, get_balanced_llm
from engines.ephemeris_engine import EphemerisEngine
from agents.stock_data_agent import StockDataAgent
from config.settings import NIFTY50_TICKERS, US_TICKERS


class TechnicalAnalyzer:
    """Calculate technical indicators"""

    def analyze(self, ticker):
        """Get technical signals for a stock"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if hist.empty:
                return {"error": "No data", "signal": "NEUTRAL", "score": 5}

            close = hist["Close"]
            volume = hist["Volume"]

            # RSI (14-day)
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = round(rsi.iloc[-1], 2)

            # Moving Averages
            sma_20 = round(close.rolling(20).mean().iloc[-1], 2)
            sma_50 = round(close.rolling(50).mean().iloc[-1], 2)
            sma_200 = round(close.rolling(200).mean().iloc[-1], 2) if len(close) >= 200 else None
            current_price = round(close.iloc[-1], 2)

            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal_line = macd.ewm(span=9).mean()
            macd_current = round(macd.iloc[-1], 2)
            signal_current = round(signal_line.iloc[-1], 2)
            macd_bullish = macd_current > signal_current

            # Volume trend
            avg_volume = volume.rolling(20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            volume_surge = current_volume > (avg_volume * 1.5)

            # Price vs moving averages
            above_sma20 = current_price > sma_20
            above_sma50 = current_price > sma_50
            above_sma200 = current_price > sma_200 if sma_200 else None

            # Calculate technical score (0-10)
            score = 5  # Start neutral

            # RSI
            if current_rsi < 30:
                score += 2  # Oversold = buy signal
            elif current_rsi < 40:
                score += 1
            elif current_rsi > 70:
                score -= 2  # Overbought = sell signal
            elif current_rsi > 60:
                score -= 1

            # Moving averages
            if above_sma20:
                score += 0.5
            if above_sma50:
                score += 0.5
            if above_sma200:
                score += 1

            # MACD
            if macd_bullish:
                score += 1
            else:
                score -= 1

            # Clamp 0-10
            score = max(0, min(10, round(score, 1)))

            # Signal
            if score >= 7:
                signal = "STRONG BUY"
            elif score >= 6:
                signal = "BUY"
            elif score >= 4:
                signal = "HOLD"
            elif score >= 3:
                signal = "SELL"
            else:
                signal = "STRONG SELL"

            return {
                "ticker": ticker,
                "current_price": current_price,
                "rsi": current_rsi,
                "rsi_signal": "Oversold" if current_rsi < 30 else "Overbought" if current_rsi > 70 else "Normal",
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "above_sma20": above_sma20,
                "above_sma50": above_sma50,
                "above_sma200": above_sma200,
                "macd": macd_current,
                "macd_signal": signal_current,
                "macd_bullish": macd_bullish,
                "volume_surge": volume_surge,
                "technical_score": score,
                "signal": signal
            }

        except Exception as e:
            return {"error": str(e), "signal": "NEUTRAL", "technical_score": 5}


class MarketScorer:
    """Score stocks based on fundamentals"""

    def __init__(self):
        self.data_agent = StockDataAgent()

    def score(self, ticker):
        """Calculate fundamental score 0-10"""
        info = self.data_agent.get_stock_info(ticker)

        if "error" in info:
            return {"error": info["error"], "score": 5, "signal": "NEUTRAL"}

        score = 5  # Start neutral

        # PE Ratio
        pe = info.get("pe_ratio", 0)
        if pe > 0:
            if pe < 15:
                score += 1.5  # Undervalued
            elif pe < 25:
                score += 0.5  # Fair
            elif pe > 40:
                score -= 1.5  # Expensive
            elif pe > 30:
                score -= 0.5

        # ROE
        roe = info.get("roe", 0)
        if roe > 0.25:
            score += 1.5
        elif roe > 0.15:
            score += 1
        elif roe > 0.10:
            score += 0.5
        elif roe < 0.05:
            score -= 1

        # Debt
        de = info.get("debt_to_equity", 0)
        if de < 0.5:
            score += 1  # Low debt
        elif de > 2:
            score -= 1  # High debt

        # Revenue Growth
        growth = info.get("revenue_growth", 0)
        if growth > 0.20:
            score += 1
        elif growth > 0.10:
            score += 0.5
        elif growth < 0:
            score -= 1

        # Profit margins
        margins = info.get("profit_margins", 0)
        if margins > 0.20:
            score += 0.5
        elif margins < 0.05:
            score -= 0.5

        score = max(0, min(10, round(score, 1)))

        if score >= 7:
            signal = "STRONG BUY"
        elif score >= 6:
            signal = "BUY"
        elif score >= 4:
            signal = "HOLD"
        elif score >= 3:
            signal = "SELL"
        else:
            signal = "STRONG SELL"

        return {
            "ticker": ticker,
            "info": info,
            "fundamental_score": score,
            "signal": signal,
            "details": {
                "pe_ratio": pe,
                "roe": roe,
                "debt_to_equity": de,
                "revenue_growth": growth,
                "profit_margins": margins
            }
        }


class JyotishScorer:
    """Score stocks/sectors based on Jyotish"""

    PLANET_SECTORS = {
        "Sun": ["PSU", "Government", "Gold", "Power"],
        "Moon": ["FMCG", "Agriculture", "Silver", "Hospitality"],
        "Mars": ["Real Estate", "Defense", "Energy", "Metals", "Engineering"],
        "Mercury": ["IT", "Banking", "Telecom", "Media", "Education"],
        "Jupiter": ["Finance", "NBFC", "Insurance", "Gold", "Legal"],
        "Venus": ["Auto", "Luxury", "Entertainment", "Textiles", "Tourism"],
        "Saturn": ["Oil", "Mining", "Infrastructure", "Construction"],
        "Rahu": ["Technology", "Crypto", "Foreign", "Pharma", "Innovation"],
        "Ketu": ["Pharma", "Chemicals", "Spiritual", "Research"]
    }

    STRONG_SIGNS = {
        "Sun": ["Leo", "Aries"],
        "Moon": ["Cancer", "Taurus"],
        "Mars": ["Aries", "Scorpio", "Capricorn"],
        "Mercury": ["Gemini", "Virgo"],
        "Jupiter": ["Sagittarius", "Pisces", "Cancer"],
        "Venus": ["Taurus", "Libra", "Pisces"],
        "Saturn": ["Capricorn", "Aquarius", "Libra"],
        "Rahu": ["Gemini", "Virgo", "Aquarius"],
        "Ketu": ["Sagittarius", "Pisces", "Scorpio"]
    }

    WEAK_SIGNS = {
        "Sun": ["Libra", "Aquarius"],
        "Moon": ["Scorpio", "Capricorn"],
        "Mars": ["Cancer", "Libra"],
        "Mercury": ["Sagittarius", "Pisces"],
        "Jupiter": ["Gemini", "Capricorn"],
        "Venus": ["Virgo", "Aries"],
        "Saturn": ["Cancer", "Leo", "Aries"],
        "Rahu": ["Sagittarius", "Scorpio"],
        "Ketu": ["Gemini", "Taurus"]
    }

    TICKER_SECTORS = {
        "RELIANCE.NS": ["Oil", "Energy", "Telecom", "Technology"],
        "TCS.NS": ["IT", "Technology"],
        "INFY.NS": ["IT", "Technology"],
        "HDFCBANK.NS": ["Banking", "Finance"],
        "ICICIBANK.NS": ["Banking", "Finance"],
        "SBIN.NS": ["Banking", "Finance", "PSU"],
        "ITC.NS": ["FMCG", "Hospitality", "Agriculture"],
        "HINDUNILVR.NS": ["FMCG"],
        "BHARTIARTL.NS": ["Telecom", "Technology"],
        "KOTAKBANK.NS": ["Banking", "Finance"],
        "LT.NS": ["Engineering", "Infrastructure", "Construction"],
        "BAJFINANCE.NS": ["Finance", "NBFC"],
        "MARUTI.NS": ["Auto"],
        "TITAN.NS": ["Luxury", "Gold"],
        "SUNPHARMA.NS": ["Pharma"],
        "TATAMOTORS.NS": ["Auto"],
        "TATASTEEL.NS": ["Metals"],
        "WIPRO.NS": ["IT", "Technology"],
        "HCLTECH.NS": ["IT", "Technology"],
        "NTPC.NS": ["Power", "PSU", "Energy"],
        "POWERGRID.NS": ["Power", "PSU", "Infrastructure"],
        "ASIANPAINT.NS": ["FMCG", "Construction"],
        "NESTLEIND.NS": ["FMCG"],
        "ADANIENT.NS": ["Infrastructure", "Energy", "Mining"],
        "JSWSTEEL.NS": ["Metals", "Infrastructure"],
        "TECHM.NS": ["IT", "Technology"],
        "AAPL": ["Technology", "Luxury"],
        "MSFT": ["Technology", "IT"],
        "GOOGL": ["Technology", "Media"],
        "AMZN": ["Technology", "FMCG"],
        "NVDA": ["Technology", "Innovation"],
        "META": ["Technology", "Media"],
        "TSLA": ["Auto", "Technology", "Energy"],
        "JPM": ["Banking", "Finance"],
    }

    def __init__(self):
        self.ephemeris = EphemerisEngine()

    def score_stock(self, ticker):
        """Score a specific stock based on Jyotish"""

        positions = self.ephemeris.get_planetary_positions()
        yogas = self.ephemeris.detect_yogas(positions)

        stock_sectors = self.TICKER_SECTORS.get(ticker, ["General"])
        score = 5  # Neutral start
        reasons = []

        # Check ruling planets for stock's sectors
        for planet, sectors in self.PLANET_SECTORS.items():
            overlap = set(stock_sectors) & set(sectors)
            if overlap:
                sign = positions[planet]["sign"]
                is_retrograde = positions[planet].get("retrograde", False)

                if sign in self.STRONG_SIGNS.get(planet, []):
                    score += 1
                    reasons.append(
                        planet + " strong in " + sign +
                        " = good for " + ", ".join(overlap)
                    )
                elif sign in self.WEAK_SIGNS.get(planet, []):
                    score -= 1
                    reasons.append(
                        planet + " weak in " + sign +
                        " = challenging for " + ", ".join(overlap)
                    )

                if is_retrograde and planet not in ["Rahu", "Ketu"]:
                    score -= 0.5
                    reasons.append(
                        planet + " retrograde = delays in " +
                        ", ".join(overlap)
                    )

        # Yoga impact
        for yoga in yogas:
            sig = yoga["significance"].lower()
            if "bull" in sig or "expansion" in sig or "wealth" in sig:
                score += 0.5
                reasons.append("Positive yoga: " + yoga["planets"])
            if "fear" in sig or "disruption" in sig or "tension" in sig:
                score -= 0.5
                reasons.append("Negative yoga: " + yoga["planets"])

        score = max(0, min(10, round(score, 1)))

        if score >= 7:
            signal = "STRONG BUY"
        elif score >= 6:
            signal = "BUY"
        elif score >= 4:
            signal = "HOLD"
        elif score >= 3:
            signal = "SELL"
        else:
            signal = "STRONG SELL"

        return {
            "ticker": ticker,
            "sectors": stock_sectors,
            "jyotish_score": score,
            "signal": signal,
            "reasons": reasons,
            "planetary_positions": positions,
            "active_yogas": yogas
        }

    def score_all_sectors(self):
        """Score all sectors based on current planets"""

        positions = self.ephemeris.get_planetary_positions()
        sector_scores = {}

        all_sectors = set()
        for sectors in self.PLANET_SECTORS.values():
            all_sectors.update(sectors)

        for sector in all_sectors:
            score = 5
            supporting = []
            opposing = []

            for planet, sectors in self.PLANET_SECTORS.items():
                if sector in sectors:
                    sign = positions[planet]["sign"]
                    if sign in self.STRONG_SIGNS.get(planet, []):
                        score += 1.5
                        supporting.append(planet + " in " + sign)
                    elif sign in self.WEAK_SIGNS.get(planet, []):
                        score -= 1.5
                        opposing.append(planet + " in " + sign)

            score = max(0, min(10, round(score, 1)))
            sector_scores[sector] = {
                "score": score,
                "supporting_planets": supporting,
                "opposing_planets": opposing,
                "signal": "BUY" if score >= 6 else "SELL" if score < 4 else "HOLD"
            }

        return dict(sorted(
            sector_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        ))


class PredictionEngine:
    """
    THE MAIN ENGINE
    Combines Market + Technical + Jyotish into final prediction
    """

    def __init__(self):
        self.market_scorer = MarketScorer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.jyotish_scorer = JyotishScorer()
        self.llm = get_balanced_llm()

    def predict_stock(self, ticker, weights=None):
        """
        Complete prediction for a single stock
        weights: how much to trust each signal
        """
        if not weights:
            weights = {
                "fundamental": 0.40,
                "technical": 0.30,
                "jyotish": 0.30
            }

        # Get all scores
        fundamental = self.market_scorer.score(ticker)
        technical = self.technical_analyzer.analyze(ticker)
        jyotish = self.jyotish_scorer.score_stock(ticker)

        # Calculate combined score
        f_score = fundamental.get("fundamental_score", 5)
        t_score = technical.get("technical_score", 5)
        j_score = jyotish.get("jyotish_score", 5)

        combined_score = round(
            f_score * weights["fundamental"] +
            t_score * weights["technical"] +
            j_score * weights["jyotish"],
            2
        )

        # Confidence based on agreement
        scores = [f_score, t_score, j_score]
        avg = sum(scores) / 3
        variance = sum((s - avg) ** 2 for s in scores) / 3
        confidence = max(30, min(95, round(100 - (variance * 8))))

        # Final signal
        if combined_score >= 7.5:
            action = "STRONG BUY"
            emoji = "🟢🟢"
        elif combined_score >= 6.5:
            action = "BUY"
            emoji = "🟢"
        elif combined_score >= 5.5:
            action = "LEAN BUY"
            emoji = "🟢"
        elif combined_score >= 4.5:
            action = "HOLD"
            emoji = "🟡"
        elif combined_score >= 3.5:
            action = "LEAN SELL"
            emoji = "🟠"
        elif combined_score >= 2.5:
            action = "SELL"
            emoji = "🔴"
        else:
            action = "STRONG SELL"
            emoji = "🔴🔴"

        return {
            "ticker": ticker,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "scores": {
                "fundamental": f_score,
                "technical": t_score,
                "jyotish": j_score,
                "combined": combined_score
            },
            "weights": weights,
            "action": action,
            "emoji": emoji,
            "confidence": confidence,
            "fundamental_data": fundamental,
            "technical_data": technical,
            "jyotish_data": jyotish
        }

    def generate_ai_report(self, prediction):
        """Use LLM to generate human-readable report"""

        prompt = "You are an expert combining financial analysis with Vedic Astrology.\n\n"
        prompt += "STOCK: " + prediction["ticker"] + "\n"
        prompt += "DATE: " + prediction["timestamp"] + "\n\n"
        prompt += "SCORES:\n"
        prompt += "- Fundamental: " + str(prediction["scores"]["fundamental"]) + "/10\n"
        prompt += "- Technical: " + str(prediction["scores"]["technical"]) + "/10\n"
        prompt += "- Jyotish: " + str(prediction["scores"]["jyotish"]) + "/10\n"
        prompt += "- COMBINED: " + str(prediction["scores"]["combined"]) + "/10\n"
        prompt += "- ACTION: " + prediction["action"] + "\n"
        prompt += "- CONFIDENCE: " + str(prediction["confidence"]) + "%\n\n"

        prompt += "FUNDAMENTAL DATA:\n"
        prompt += json.dumps(prediction["fundamental_data"].get("details", {}), indent=2) + "\n\n"

        prompt += "TECHNICAL DATA:\n"
        tech = prediction["technical_data"]
        prompt += "RSI: " + str(tech.get("rsi", "N/A")) + "\n"
        prompt += "MACD Bullish: " + str(tech.get("macd_bullish", "N/A")) + "\n"
        prompt += "Above SMA50: " + str(tech.get("above_sma50", "N/A")) + "\n\n"

        prompt += "JYOTISH DATA:\n"
        for reason in prediction["jyotish_data"].get("reasons", []):
            prompt += "- " + reason + "\n"

        prompt += "\n## Generate a CLEAR, ACTIONABLE report:\n\n"
        prompt += "### 1. VERDICT: " + prediction["action"] + "\n"
        prompt += "Explain WHY in 2-3 sentences.\n\n"
        prompt += "### 2. ENTRY STRATEGY\n"
        prompt += "- Exact entry price range\n"
        prompt += "- Stop loss level\n"
        prompt += "- Target prices (short/medium/long term)\n\n"
        prompt += "### 3. WHERE ALL SIGNALS AGREE\n"
        prompt += "List points where fundamental + technical + jyotish align.\n\n"
        prompt += "### 4. WARNING SIGNALS\n"
        prompt += "Any conflicting signals to watch.\n\n"
        prompt += "### 5. JYOTISH TIMING\n"
        prompt += "- Best dates to execute this trade\n"
        prompt += "- Dates to avoid\n"
        prompt += "- Next major planetary event affecting this stock\n\n"
        prompt += "### 6. RISK MANAGEMENT\n"
        prompt += "- Position size suggestion (% of portfolio)\n"
        prompt += "- Risk-reward ratio\n\n"
        prompt += "Keep it concise and actionable. Trader-friendly language.\n"
        prompt += "Disclaimer: Not financial advice.\n"

        return self.llm(prompt)

    def scan_market(self, tickers=None, top_n=10):
        """Scan multiple stocks and rank them"""

        if not tickers:
            tickers = NIFTY50_TICKERS[:20]  # Top 20 Nifty stocks

        results = []

        for ticker in tickers:
            try:
                pred = self.predict_stock(ticker)
                results.append(pred)
            except Exception:
                continue

        # Sort by combined score
        results.sort(
            key=lambda x: x["scores"]["combined"],
            reverse=True
        )

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_scanned": len(results),
            "top_buys": [r for r in results if r["scores"]["combined"] >= 6][:top_n],
            "top_sells": [r for r in results if r["scores"]["combined"] < 4][:top_n],
            "all_results": results
        }

    def generate_scan_report(self, scan_results):
        """AI report for market scan"""

        top_buys = scan_results["top_buys"]
        top_sells = scan_results["top_sells"]

        prompt = "You are a market strategist combining finance + Vedic Astrology.\n\n"
        prompt += "MARKET SCAN RESULTS (" + scan_results["timestamp"] + ")\n"
        prompt += "Stocks scanned: " + str(scan_results["total_scanned"]) + "\n\n"

        prompt += "## TOP BUY SIGNALS:\n"
        for stock in top_buys[:5]:
            prompt += "- " + stock["ticker"]
            prompt += " | Combined: " + str(stock["scores"]["combined"])
            prompt += " | F:" + str(stock["scores"]["fundamental"])
            prompt += " T:" + str(stock["scores"]["technical"])
            prompt += " J:" + str(stock["scores"]["jyotish"])
            prompt += " | " + stock["action"] + "\n"

        prompt += "\n## TOP SELL SIGNALS:\n"
        for stock in top_sells[:5]:
            prompt += "- " + stock["ticker"]
            prompt += " | Combined: " + str(stock["scores"]["combined"])
            prompt += " | " + stock["action"] + "\n"

        prompt += "\n## Generate ACTIONABLE trading plan:\n\n"
        prompt += "### TODAY'S TOP 5 BUYS\n"
        prompt += "For each: Why buy, entry price, target, stop loss\n\n"
        prompt += "### TODAY'S STOCKS TO AVOID/SELL\n"
        prompt += "For each: Why avoid, key risk\n\n"
        prompt += "### JYOTISH MARKET TIMING\n"
        prompt += "Best trading days this week based on planetary positions\n\n"
        prompt += "### PORTFOLIO ALLOCATION\n"
        prompt += "How to distribute capital among top picks\n\n"
        prompt += "Be specific with numbers. Trader-friendly.\n"
        prompt += "Disclaimer: Not financial advice.\n"

        return self.llm(prompt)


if __name__ == "__main__":
    print("Testing Prediction Engine...")

    engine = PredictionEngine()

    # Single stock prediction
    print("\n=== RELIANCE.NS PREDICTION ===")
    pred = engine.predict_stock("RELIANCE.NS")
    print("Fundamental: " + str(pred["scores"]["fundamental"]) + "/10")
    print("Technical:   " + str(pred["scores"]["technical"]) + "/10")
    print("Jyotish:     " + str(pred["scores"]["jyotish"]) + "/10")
    print("Combined:    " + str(pred["scores"]["combined"]) + "/10")
    print("Action:      " + pred["emoji"] + " " + pred["action"])
    print("Confidence:  " + str(pred["confidence"]) + "%")
