"""
Signal Scorer — Master Combiner
================================
Combines ALL Jyotish signals into one score.
Every data point is real-time computed. Nothing hardcoded.

Sources:
1. General planetary strength (Graha Bala + Yogas + BNN)
2. Company birth chart transits (company-specific)
3. Sector Karaka strength (sector-specific)
4. Active events (conjunctions, retrogrades, eclipses, moon phase)

All weights adjustable via backtest.
"""

from datetime import datetime
from engines.realtime_astro import RealtimeAstroEngine
from engines.vedic_core import BPHSSystem, BNNSystem


class SignalScorer:
    """Combines all Jyotish signals with real-time data."""

    DEFAULT_WEIGHTS = {
        "general_jyotish": 0.20,
        "company_transit": 0.30,
        "sector_karaka": 0.20,
        "events": 0.30,
    }

    def __init__(self):
        self.astro = RealtimeAstroEngine()
        self.bphs = BPHSSystem()
        self.bnn = BNNSystem()

    def _positions_for_vedic_core(self, positions):
        """Convert realtime_astro positions to format vedic_core expects."""
        converted = {}
        for planet, data in positions.items():
            converted[planet] = {
                "sign": data["sign"],
                "degree": data["degree"],
                "retrograde": data.get("retrograde", False),
                "nakshatra": data.get("nakshatra", ""),
            }
        return converted

    def get_general_score(self, positions_vc):
        """General market Jyotish score from BPHS + BNN."""
        score = 50

        for planet, data in positions_vc.items():
            bala = self.bphs.calculate_graha_bala(
                planet, data["sign"], data["degree"], positions_vc
            )
            if planet in ["Jupiter", "Venus", "Mercury"]:
                if bala["status"] in ["VERY_STRONG", "STRONG"]: score += 3
                elif bala["status"] == "VERY_WEAK": score -= 3
            if planet == "Moon":
                if bala["status"] in ["VERY_STRONG", "STRONG"]: score += 4
                elif bala["status"] == "VERY_WEAK": score -= 4
            if planet in ["Saturn", "Mars"]:
                if bala["status"] == "VERY_WEAK": score -= 2

        dhana_yogas = self.bphs.detect_dhana_yogas(positions_vc)
        for y in dhana_yogas:
            if y["strength"] in ["VERY_STRONG", "STRONG"]: score += 3
            elif y["strength"] in ["NEGATIVE", "VERY_NEGATIVE"]: score -= 4

        bnn_result = self.bnn.get_market_nakshatra_score(positions_vc)
        bnn_val = bnn_result.get("bnn_score", 5)
        score += (bnn_val - 5) * 2

        return max(0, min(100, round(score, 1)))

    def get_company_transit_score(self, ticker, positions):
        """Company birth chart transit score."""
        try:
            from engines.company_chart import CompanyChartEngine
            cce = CompanyChartEngine()
            transit = cce.get_current_transits_over_natal(ticker)
            if "error" not in transit:
                return transit["transit_score"], transit
            return 50, {"available": False, "reason": transit.get("error", "")}
        except Exception as e:
            return 50, {"available": False, "reason": str(e)}

    def get_sector_karaka_score(self, ticker):
        """Sector karaka planet strength."""
        try:
            from engines.sector_karaka import SectorKarakaEngine
            ske = SectorKarakaEngine()
            karaka = ske.get_ticker_karaka_strength(ticker)
            if karaka.get("karaka_planets"):
                smap = {"VERY_STRONG": 85, "STRONG": 70, "MODERATE": 55, "WEAK": 35, "VERY_WEAK": 20}
                scores = [smap.get(kp["status"], 50) for kp in karaka["karaka_planets"]]
                return round(sum(scores) / len(scores), 1), karaka
            return 50, {"available": False}
        except Exception:
            return 50, {"available": False}

    def get_event_score(self, snapshot):
        """Score from active astronomical events."""
        score = 50

        # Retrogrades
        for r in snapshot.get("retrogrades", []):
            planet = r["planet"]
            if planet == "Mercury": score -= 4
            elif planet == "Jupiter": score -= 5
            elif planet == "Venus": score -= 3
            elif planet == "Saturn": score -= 2
            elif planet == "Mars": score -= 3

        # Conjunctions
        for c in snapshot.get("conjunctions", []):
            pair = frozenset([c["planet1"], c["planet2"]])
            tight = c.get("tight", False)

            if pair == frozenset(["Jupiter", "Venus"]):
                score += 8 if tight else 4
            elif pair == frozenset(["Jupiter", "Mercury"]):
                score += 5 if tight else 3
            elif pair == frozenset(["Saturn", "Mars"]):
                score -= 8 if tight else 4
            elif pair == frozenset(["Saturn", "Rahu"]):
                score -= 7 if tight else 4
            elif pair == frozenset(["Sun", "Rahu"]):
                score -= 4 if tight else 2
            elif pair == frozenset(["Moon", "Rahu"]):
                score -= 5 if tight else 3
            elif pair == frozenset(["Venus", "Mars"]):
                score += 3 if tight else 1

        # Eclipses
        for e in snapshot.get("upcoming_eclipses", []):
            days = e.get("days_away", 99)
            if days <= 3: score -= 6
            elif days <= 7: score -= 3
            elif days <= 15: score -= 1

        # Moon phase
        moon = snapshot.get("moon_phase", {})
        bias = moon.get("market_bias", "")
        if bias == "bullish": score += 3
        elif bias == "peak optimism": score += 4
        elif bias == "bearish": score -= 3
        elif bias == "fear/bottoming": score += 1  # Contrarian
        elif bias == "distribution": score -= 2

        return max(0, min(100, round(score, 1)))

    def get_full_score(self, ticker):
        """
        MAIN FUNCTION: Complete Jyotish analysis for a ticker.
        All data real-time. Returns breakdown + combined score.
        """
        # Get real-time sky snapshot
        snapshot = self.astro.get_complete_snapshot()
        positions = snapshot["positions"]
        positions_vc = self._positions_for_vedic_core(positions)

        scores = {}
        details = {}

        # 1. General Jyotish
        scores["general_jyotish"] = self.get_general_score(positions_vc)
        details["general_jyotish"] = {"description": "Planetary strength + Yogas + BNN"}

        # 2. Company transit
        ct_score, ct_detail = self.get_company_transit_score(ticker, positions)
        scores["company_transit"] = ct_score
        details["company_transit"] = ct_detail

        # 3. Sector karaka
        sk_score, sk_detail = self.get_sector_karaka_score(ticker)
        scores["sector_karaka"] = sk_score
        details["sector_karaka"] = sk_detail

        # 4. Events
        scores["events"] = self.get_event_score(snapshot)
        details["events"] = {
            "retrogrades": snapshot["retrogrades"],
            "conjunctions": snapshot["conjunctions"],
            "eclipses": snapshot["upcoming_eclipses"],
            "moon_phase": snapshot["moon_phase"],
        }

        # ── DYNAMIC WEIGHT ADJUSTMENT ──
        weights = self.DEFAULT_WEIGHTS.copy()

        has_company = details.get("company_transit", {}).get("available") is not False
        has_sector = details.get("sector_karaka", {}).get("available") is not False

        if not has_company:
            extra = weights["company_transit"]
            weights["company_transit"] = 0
            weights["general_jyotish"] += extra * 0.4
            weights["events"] += extra * 0.4
            weights["sector_karaka"] += extra * 0.2

        if not has_sector:
            extra = weights["sector_karaka"]
            weights["sector_karaka"] = 0
            weights["general_jyotish"] += extra * 0.5
            weights["events"] += extra * 0.5

        # Normalize
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {k: round(v / total_w, 3) for k, v in weights.items()}

        # Combined
        combined = sum(scores.get(k, 50) * weights.get(k, 0) for k in scores)
        combined = max(0, min(100, round(combined, 1)))

        signal = (
            "STRONG_BUY" if combined >= 72 else
            "BUY" if combined >= 58 else
            "NEUTRAL" if combined >= 42 else
            "SELL" if combined >= 28 else
            "STRONG_SELL"
        )

        # Extra info
        moon = snapshot.get("moon_phase", {})
        dhana_yogas = self.bphs.detect_dhana_yogas(positions_vc)
        bnn_val = self.bnn.get_market_nakshatra_score(positions_vc).get("bnn_score", 5)

        return {
            "ticker": ticker,
            "combined_score": combined,
            "signal": signal,
            "scores": scores,
            "weights": weights,
            "details": details,
            "sky_snapshot": {
                "timestamp": snapshot["timestamp"],
                "moon_nakshatra": moon.get("moon_nakshatra", "-"),
                "moon_sign": moon.get("moon_sign", "-"),
                "moon_phase": moon.get("phase", "-"),
                "tithi": moon.get("tithi", 0),
                "market_bias": moon.get("market_bias", "-"),
                "retrograde_count": snapshot["retrograde_count"],
                "retrogrades": [r["planet"] for r in snapshot["retrogrades"]],
                "conjunction_count": len(snapshot["conjunctions"]),
                "eclipse_soon": len(snapshot["upcoming_eclipses"]) > 0,
            },
            "dhana_yogas": dhana_yogas,
            "bnn_score": bnn_val,
            "positions": {
                p: {
                    "sign": d["sign"],
                    "degree": d["degree"],
                    "nakshatra": d["nakshatra"],
                    "retrograde": d["retrograde"],
                }
                for p, d in positions.items()
            },
        }
