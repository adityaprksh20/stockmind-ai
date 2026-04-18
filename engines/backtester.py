"""
Backtesting Engine - Validates if Jyotish actually improves predictions
Compares: Fundamental-only vs Fundamental+Technical vs Fundamental+Technical+Jyotish
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from engines.ephemeris_engine import EphemerisEngine
from engines.vedic_core import BPHSSystem, BNNSystem


class MarketBacktester:
    """
    Tests if Jyotish signals correlate with actual market movements.

    Methodology:
    1. For each historical date, calculate Jyotish scores
    2. Get actual market returns for the NEXT period
    3. Measure correlation between Jyotish score and actual returns
    4. Compare accuracy: with Jyotish vs without
    """

    def __init__(self):
        self.ephemeris = EphemerisEngine()
        self.bphs = BPHSSystem()
        self.bnn = BNNSystem()

    def get_historical_returns(self, ticker, start_date, end_date):
        """Get actual stock returns for a period"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                return None

            returns = {}

            # Daily returns
            hist["daily_return"] = hist["Close"].pct_change()

            # Weekly returns (5 trading days forward)
            hist["weekly_forward_return"] = (
                hist["Close"].shift(-5) / hist["Close"] - 1
            )

            # Monthly returns (21 trading days forward)
            hist["monthly_forward_return"] = (
                hist["Close"].shift(-21) / hist["Close"] - 1
            )

            return hist

        except Exception as e:
            print("Error fetching " + ticker + ": " + str(e))
            return None

    def calculate_jyotish_score_for_date(self, date):
        """
        Calculate a numerical Jyotish score for a specific date.
        This is the KEY function - converts astrology to a number.
        """

        positions = self.ephemeris.get_planetary_positions(date)

        score = 50  # Start neutral (0-100 scale)
        components = {}

        # ==============================
        # COMPONENT 1: BPHS Graha Bala
        # ==============================
        bala_score = 0
        for planet, data in positions.items():
            bala = self.bphs.calculate_graha_bala(
                planet, data["sign"], data["degree"], positions
            )

            # Benefics strong = positive for market
            if planet in ["Jupiter", "Venus", "Mercury"]:
                if bala["status"] in ["VERY_STRONG", "STRONG"]:
                    bala_score += 3
                elif bala["status"] in ["VERY_WEAK"]:
                    bala_score -= 3

            # Malefics strong = mixed (Saturn strong = discipline)
            if planet in ["Saturn", "Mars"]:
                if bala["status"] == "VERY_WEAK":
                    bala_score -= 2  # Weak malefics cause chaos
                elif bala["status"] == "VERY_STRONG":
                    bala_score += 1  # Strong malefics = controlled

            # Moon strong = positive sentiment
            if planet == "Moon":
                if bala["status"] in ["VERY_STRONG", "STRONG"]:
                    bala_score += 4
                elif bala["status"] in ["VERY_WEAK"]:
                    bala_score -= 4

        components["bphs_bala"] = bala_score

        # ==============================
        # COMPONENT 2: Dhana Yogas
        # ==============================
        dhana_yogas = self.bphs.detect_dhana_yogas(positions)
        yoga_score = 0

        for yoga in dhana_yogas:
            if yoga["strength"] == "VERY_STRONG":
                yoga_score += 5
            elif yoga["strength"] == "STRONG":
                yoga_score += 3
            elif yoga["strength"] == "MODERATE":
                yoga_score += 1
            elif yoga["strength"] == "NEGATIVE":
                yoga_score -= 4
            elif yoga["strength"] == "VERY_NEGATIVE":
                yoga_score -= 6

        components["dhana_yogas"] = yoga_score

        # ==============================
        # COMPONENT 3: BNN Nakshatra Score
        # ==============================
        bnn_result = self.bnn.get_market_nakshatra_score(positions)
        bnn_score = bnn_result.get("bnn_score", 5)
        # Convert 0-10 to -5 to +5
        nakshatra_score = (bnn_score - 5) * 2

        components["bnn_nakshatra"] = nakshatra_score

        # ==============================
        # COMPONENT 4: Moon Nakshatra Strength
        # ==============================
        moon_analysis = self.bnn.get_moon_nakshatra_analysis(positions)
        moon_nak_score = 0
        if "error" not in moon_analysis:
            moon_strength = moon_analysis.get("strength", 5)
            moon_nak_score = (moon_strength - 5) * 1.5

        components["moon_nakshatra"] = moon_nak_score

        # ==============================
        # COMPONENT 5: Retrograde Count
        # ==============================
        retro_count = sum(
            1 for p, d in positions.items()
            if d.get("retrograde") and p not in ["Rahu", "Ketu"]
        )
        retro_score = -retro_count * 2  # Each retrograde = negative

        components["retrograde"] = retro_score

        # ==============================
        # COMBINE ALL COMPONENTS
        # ==============================
        total_adjustment = (
            bala_score * 0.25 +
            yoga_score * 0.30 +
            nakshatra_score * 0.20 +
            moon_nak_score * 0.15 +
            retro_score * 0.10
        )

        score = 50 + total_adjustment
        score = max(0, min(100, round(score, 2)))

        return {
            "date": date.strftime("%Y-%m-%d"),
            "jyotish_score": score,
            "components": components,
            "signal": (
                "STRONG_BUY" if score >= 70 else
                "BUY" if score >= 60 else
                "NEUTRAL" if score >= 40 else
                "SELL" if score >= 30 else
                "STRONG_SELL"
            ),
            "dhana_yogas_active": len(dhana_yogas),
            "retrogrades": retro_count
        }

    def backtest_stock(self, ticker, months_back=12, holding_period="weekly"):
        """
        Main backtest function.
        Compares Jyotish signals with actual returns.
        """

        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)

        print("Backtesting " + ticker + " from " +
              start_date.strftime("%Y-%m-%d") + " to " +
              end_date.strftime("%Y-%m-%d"))

        # Get actual returns
        hist = self.get_historical_returns(
            ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        if hist is None or hist.empty:
            return {"error": "No data for " + ticker}

        # Calculate Jyotish score for each trading day
        results = []
        dates = hist.index.tolist()

        # Sample every 5th trading day (weekly) for speed
        sample_dates = dates[::5]

        print("Calculating Jyotish scores for " +
              str(len(sample_dates)) + " dates...")

        for i, date in enumerate(sample_dates):
            if i % 10 == 0:
                print("  Processing " + str(i) + "/" +
                      str(len(sample_dates)) + "...")

            dt = date.to_pydatetime().replace(tzinfo=None)

            try:
                # Jyotish score
                jyotish = self.calculate_jyotish_score_for_date(dt)

                # Actual return
                if holding_period == "weekly":
                    actual_return = hist.loc[date, "weekly_forward_return"]
                else:
                    actual_return = hist.loc[date, "monthly_forward_return"]

                if pd.notna(actual_return):
                    results.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "jyotish_score": jyotish["jyotish_score"],
                        "signal": jyotish["signal"],
                        "actual_return": round(actual_return * 100, 4),
                        "components": jyotish["components"],
                        "dhana_yogas": jyotish["dhana_yogas_active"],
                        "retrogrades": jyotish["retrogrades"]
                    })

            except Exception as e:
                continue

        if not results:
            return {"error": "No results generated"}

        # ==============================
        # ANALYZE RESULTS
        # ==============================
        df = pd.DataFrame(results)

        # 1. Correlation
        correlation = df["jyotish_score"].corr(df["actual_return"])

        # 2. Signal Accuracy
        # When Jyotish says BUY (score >= 60), was return positive?
        buy_signals = df[df["jyotish_score"] >= 60]
        sell_signals = df[df["jyotish_score"] < 40]
        neutral_signals = df[
            (df["jyotish_score"] >= 40) & (df["jyotish_score"] < 60)
        ]

        buy_accuracy = 0
        if len(buy_signals) > 0:
            buy_accuracy = round(
                (buy_signals["actual_return"] > 0).sum() /
                len(buy_signals) * 100, 2
            )

        sell_accuracy = 0
        if len(sell_signals) > 0:
            sell_accuracy = round(
                (sell_signals["actual_return"] < 0).sum() /
                len(sell_signals) * 100, 2
            )

        # 3. Average returns by signal
        avg_return_buy = round(buy_signals["actual_return"].mean(), 4) if len(buy_signals) > 0 else 0
        avg_return_sell = round(sell_signals["actual_return"].mean(), 4) if len(sell_signals) > 0 else 0
        avg_return_neutral = round(neutral_signals["actual_return"].mean(), 4) if len(neutral_signals) > 0 else 0
        avg_return_all = round(df["actual_return"].mean(), 4)

        # 4. Baseline: Buy and hold return
        buy_hold_return = round(
            (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100, 2
        )

        # 5. Jyotish strategy return (simplified)
        # Only invested when Jyotish says BUY
        if len(buy_signals) > 0:
            jyotish_strategy_return = round(
                buy_signals["actual_return"].sum(), 2
            )
        else:
            jyotish_strategy_return = 0

        # 6. Component correlations
        component_corr = {}
        for comp in ["bphs_bala", "dhana_yogas", "bnn_nakshatra",
                      "moon_nakshatra", "retrograde"]:
            comp_values = [r["components"].get(comp, 0) for r in results]
            comp_series = pd.Series(comp_values)
            component_corr[comp] = round(
                comp_series.corr(df["actual_return"]), 4
            )

        return {
            "ticker": ticker,
            "period": start_date.strftime("%Y-%m-%d") + " to " + end_date.strftime("%Y-%m-%d"),
            "holding_period": holding_period,
            "total_signals": len(results),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "neutral_signals": len(neutral_signals),

            "correlation": round(correlation, 4),

            "buy_accuracy": buy_accuracy,
            "sell_accuracy": sell_accuracy,

            "avg_return_on_buy_signal": avg_return_buy,
            "avg_return_on_sell_signal": avg_return_sell,
            "avg_return_on_neutral": avg_return_neutral,
            "avg_return_overall": avg_return_all,

            "buy_hold_return": buy_hold_return,
            "jyotish_strategy_return": jyotish_strategy_return,
            "jyotish_outperformance": round(
                jyotish_strategy_return - buy_hold_return, 2
            ),

            "component_correlations": component_corr,

            "verdict": self._interpret_results(
                correlation, buy_accuracy, sell_accuracy,
                avg_return_buy, avg_return_sell, buy_hold_return,
                jyotish_strategy_return
            ),

            "raw_data": results
        }

    def _interpret_results(self, correlation, buy_acc, sell_acc,
                           avg_buy, avg_sell, buy_hold, jyotish_return):
        """Honest interpretation of backtest results"""

        verdict = {
            "correlation_strength": "",
            "signal_quality": "",
            "adds_value": False,
            "recommended_weight": 0,
            "honest_assessment": ""
        }

        # Correlation interpretation
        abs_corr = abs(correlation)
        if abs_corr > 0.3:
            verdict["correlation_strength"] = "MEANINGFUL"
        elif abs_corr > 0.15:
            verdict["correlation_strength"] = "WEAK"
        elif abs_corr > 0.05:
            verdict["correlation_strength"] = "VERY_WEAK"
        else:
            verdict["correlation_strength"] = "NONE"

        # Signal quality
        avg_accuracy = (buy_acc + sell_acc) / 2
        if avg_accuracy > 60:
            verdict["signal_quality"] = "USEFUL"
        elif avg_accuracy > 52:
            verdict["signal_quality"] = "MARGINAL"
        else:
            verdict["signal_quality"] = "NOT_USEFUL"

        # Does it add value?
        if jyotish_return > buy_hold and avg_accuracy > 55:
            verdict["adds_value"] = True
            verdict["recommended_weight"] = min(30, int(avg_accuracy - 50) * 3)
        elif avg_accuracy > 52:
            verdict["adds_value"] = True
            verdict["recommended_weight"] = min(15, int(avg_accuracy - 50) * 2)
        else:
            verdict["adds_value"] = False
            verdict["recommended_weight"] = 0

        # Honest assessment
        if verdict["adds_value"] and verdict["correlation_strength"] == "MEANINGFUL":
            verdict["honest_assessment"] = (
                "POSITIVE: Jyotish signals show meaningful correlation with "
                "market returns. The signal appears to add value beyond random "
                "chance. Recommended weight: " +
                str(verdict["recommended_weight"]) + "% in combined model."
            )
        elif verdict["adds_value"]:
            verdict["honest_assessment"] = (
                "MARGINAL: Jyotish signals show slight edge over random. "
                "May add small value when combined with fundamental and "
                "technical analysis. Use with LOW weight: " +
                str(verdict["recommended_weight"]) + "%."
            )
        else:
            verdict["honest_assessment"] = (
                "NEGATIVE: Jyotish signals do NOT show meaningful correlation "
                "with actual market returns for this stock/period. "
                "Recommended weight: 0%. Rely on fundamental and technical "
                "analysis instead. Jyotish may still have value for timing "
                "or as a contrarian indicator - more testing needed."
            )

        return verdict

    def backtest_multiple(self, tickers, months_back=12):
        """Backtest across multiple stocks"""

        all_results = {}
        summary = {
            "total_stocks": 0,
            "jyotish_added_value": 0,
            "jyotish_no_value": 0,
            "avg_correlation": 0,
            "avg_buy_accuracy": 0,
            "avg_sell_accuracy": 0,
            "stocks_outperformed": 0
        }

        correlations = []
        buy_accs = []
        sell_accs = []

        for ticker in tickers:
            print("\n" + "=" * 50)
            print("Backtesting: " + ticker)
            print("=" * 50)

            result = self.backtest_stock(ticker, months_back)

            if "error" in result:
                print("  Skipped: " + result["error"])
                continue

            all_results[ticker] = result
            summary["total_stocks"] += 1

            if result["verdict"]["adds_value"]:
                summary["jyotish_added_value"] += 1
            else:
                summary["jyotish_no_value"] += 1

            if result["jyotish_outperformance"] > 0:
                summary["stocks_outperformed"] += 1

            correlations.append(result["correlation"])
            buy_accs.append(result["buy_accuracy"])
            sell_accs.append(result["sell_accuracy"])

        if correlations:
            summary["avg_correlation"] = round(
                sum(correlations) / len(correlations), 4
            )
            summary["avg_buy_accuracy"] = round(
                sum(buy_accs) / len(buy_accs), 2
            )
            summary["avg_sell_accuracy"] = round(
                sum(sell_accs) / len(sell_accs), 2
            )

        # Overall verdict
        if summary["jyotish_added_value"] > summary["jyotish_no_value"]:
            summary["overall_verdict"] = (
                "POSITIVE: Jyotish signals added value for " +
                str(summary["jyotish_added_value"]) + "/" +
                str(summary["total_stocks"]) + " stocks tested."
            )
        else:
            summary["overall_verdict"] = (
                "INCONCLUSIVE/NEGATIVE: Jyotish signals added value for only " +
                str(summary["jyotish_added_value"]) + "/" +
                str(summary["total_stocks"]) + " stocks. "
                "Consider reducing Jyotish weight in combined model."
            )

        return {
            "summary": summary,
            "individual_results": all_results
        }

    def print_backtest_report(self, result):
        """Pretty print backtest results"""

        if "error" in result:
            print("ERROR: " + result["error"])
            return

        print("\n" + "=" * 60)
        print("BACKTEST REPORT: " + result["ticker"])
        print("Period: " + result["period"])
        print("Holding: " + result["holding_period"])
        print("=" * 60)

        print("\n--- SIGNAL DISTRIBUTION ---")
        print("Total signals: " + str(result["total_signals"]))
        print("BUY signals:   " + str(result["buy_signals"]))
        print("SELL signals:  " + str(result["sell_signals"]))
        print("NEUTRAL:       " + str(result["neutral_signals"]))

        print("\n--- CORRELATION ---")
        print("Jyotish Score vs Returns: " + str(result["correlation"]))
        print("Strength: " + result["verdict"]["correlation_strength"])

        print("\n--- ACCURACY ---")
        print("BUY signal accuracy:  " + str(result["buy_accuracy"]) + "%")
        print("SELL signal accuracy: " + str(result["sell_accuracy"]) + "%")

        print("\n--- RETURNS ---")
        print("Avg return on BUY signal:  " + str(result["avg_return_on_buy_signal"]) + "%")
        print("Avg return on SELL signal: " + str(result["avg_return_on_sell_signal"]) + "%")
        print("Avg return overall:        " + str(result["avg_return_overall"]) + "%")
        print("Buy & Hold return:         " + str(result["buy_hold_return"]) + "%")
        print("Jyotish strategy return:   " + str(result["jyotish_strategy_return"]) + "%")
        print("Outperformance:            " + str(result["jyotish_outperformance"]) + "%")

        print("\n--- COMPONENT ANALYSIS ---")
        print("Which Jyotish components correlate with returns:")
        for comp, corr in result["component_correlations"].items():
            indicator = "✅" if abs(corr) > 0.1 else "❌"
            print("  " + indicator + " " + comp + ": " + str(corr))

        print("\n--- VERDICT ---")
        v = result["verdict"]
        print("Adds Value: " + str(v["adds_value"]))
        print("Recommended Weight: " + str(v["recommended_weight"]) + "%")
        print("Assessment: " + v["honest_assessment"])


if __name__ == "__main__":
    print("=" * 60)
    print("JYOTISH BACKTEST - PROOF OR DISPROOF")
    print("=" * 60)
    print()
    print("This will test if Jyotish signals actually correlate")
    print("with real market returns. Be prepared for honest results.")
    print()

    bt = MarketBacktester()

    # Test single stock first
    print("Testing RELIANCE.NS (last 12 months)...")
    result = bt.backtest_stock("RELIANCE.NS", months_back=12)
    bt.print_backtest_report(result)
