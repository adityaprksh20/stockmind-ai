"""
Sector Karaka Engine
====================
In Jyotish, each planet is karaka (significator) of specific industries.
When a karaka planet is strong, its sectors outperform.
When weak/afflicted, those sectors underperform.

This creates SECTOR ROTATION signals based on planetary strength.
"""

from datetime import datetime
from engines.ephemeris_engine import EphemerisEngine
from engines.vedic_core import BPHSSystem

# ── PLANET → SECTOR MAPPING (Classical Jyotish) ────────
# Based on BPHS, Jataka Parijata, and modern adaptations
PLANET_SECTOR_MAP = {
    "Sun": {
        "sectors": ["Government", "Power & Energy", "Healthcare", "Gold & Metals"],
        "tickers_india": ["NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "SUNPHARMA.NS"],
        "tickers_us": ["XLE", "GDX", "XLV", "GLD"],
        "karaka_of": "Authority, government, vitality, gold",
    },
    "Moon": {
        "sectors": ["FMCG", "Water & Beverages", "Agriculture", "Hospitality", "Real Estate"],
        "tickers_india": ["HINDUNILVR.NS", "ITC.NS", "TATACONSUM.NS", "GODREJCP.NS"],
        "tickers_us": ["XLP", "KO", "PG", "PEP"],
        "karaka_of": "Public sentiment, liquids, nourishment, comfort",
    },
    "Mars": {
        "sectors": ["Defense", "Real Estate", "Steel & Metals", "Automobiles", "Surgery/Pharma"],
        "tickers_india": ["TATASTEEL.NS", "JSWSTEEL.NS", "MARUTI.NS", "BEL.NS"],
        "tickers_us": ["XLI", "LMT", "BA", "SLX"],
        "karaka_of": "Energy, competition, engineering, land",
    },
    "Mercury": {
        "sectors": ["IT & Software", "Communications", "Media", "Education", "Fintech", "Trading"],
        "tickers_india": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
        "tickers_us": ["XLK", "QQQ", "GOOGL", "META"],
        "karaka_of": "Intelligence, communication, commerce, data",
    },
    "Jupiter": {
        "sectors": ["Banking & Finance", "Insurance", "Education", "Legal", "Religious Tourism"],
        "tickers_india": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BAJFINANCE.NS"],
        "tickers_us": ["XLF", "JPM", "V", "MA"],
        "karaka_of": "Wealth, expansion, wisdom, law, banking",
    },
    "Venus": {
        "sectors": ["Luxury", "Entertainment", "Fashion", "Automobiles", "Sugar", "Film"],
        "tickers_india": ["TITAN.NS", "MARUTI.NS", "ASIANPAINT.NS", "TRENT.NS"],
        "tickers_us": ["XLY", "LVMUY", "NKE", "DIS"],
        "karaka_of": "Luxury, beauty, vehicles, pleasure, arts",
    },
    "Saturn": {
        "sectors": ["Infrastructure", "Mining", "Oil & Gas", "Construction", "Agriculture Labor"],
        "tickers_india": ["LT.NS", "RELIANCE.NS", "ULTRACEMCO.NS", "ADANIENT.NS"],
        "tickers_us": ["XLB", "CAT", "DE", "XOM"],
        "karaka_of": "Hard work, structure, old industries, mining",
    },
    "Rahu": {
        "sectors": ["Technology", "Pharma", "Foreign Companies", "Crypto", "Aviation", "Disruptors"],
        "tickers_india": ["INFY.NS", "DRREDDY.NS", "INDIGO.NS", "ZOMATO.NS"],
        "tickers_us": ["ARKK", "TSLA", "NVDA", "COIN"],
        "karaka_of": "Innovation, disruption, foreign, unconventional",
    },
    "Ketu": {
        "sectors": ["Spirituality", "Alternative Medicine", "Legacy Tech", "Defense Research"],
        "tickers_india": ["DABUR.NS", "PATANJALI", "BEL.NS", "HAL.NS"],
        "tickers_us": ["RTX", "GD", "NOC"],
        "karaka_of": "Detachment, research, mysticism, past karma",
    },
}


class SectorKarakaEngine:
    """Generates sector rotation signals based on planetary strength."""

    def __init__(self):
        self.eph = EphemerisEngine()
        self.bphs = BPHSSystem()

    def get_sector_signals(self):
        """
        Calculate which sectors are favored/unfavored right now
        based on their karaka planet's strength.
        """
        now = datetime.now()
        positions = self.eph.get_planetary_positions(now)

        sector_signals = []

        for planet, sector_data in PLANET_SECTOR_MAP.items():
            if planet not in positions:
                continue

            pos = positions[planet]
            bala = self.bphs.calculate_graha_bala(
                planet, pos["sign"], pos["degree"], positions
            )

            # Score: -10 to +10
            strength_map = {
                "VERY_STRONG": 10,
                "STRONG": 6,
                "MODERATE": 2,
                "WEAK": -4,
                "VERY_WEAK": -8,
            }
            strength_score = strength_map.get(bala["status"], 0)

            # Retrograde penalty
            if pos.get("retrograde") and planet not in ["Rahu", "Ketu"]:
                strength_score -= 3

            # Determine signal
            if strength_score >= 6:
                signal = "OVERWEIGHT"
                signal_color = "green"
            elif strength_score >= 2:
                signal = "SLIGHT_OW"
                signal_color = "lightgreen"
            elif strength_score >= -2:
                signal = "NEUTRAL"
                signal_color = "yellow"
            elif strength_score >= -5:
                signal = "SLIGHT_UW"
                signal_color = "orange"
            else:
                signal = "UNDERWEIGHT"
                signal_color = "red"

            sector_signals.append({
                "planet": planet,
                "sign": pos["sign"],
                "degree": round(pos["degree"], 1),
                "retrograde": pos.get("retrograde", False),
                "strength_status": bala["status"],
                "strength_score": strength_score,
                "signal": signal,
                "signal_color": signal_color,
                "sectors": sector_data["sectors"],
                "tickers_india": sector_data["tickers_india"],
                "tickers_us": sector_data["tickers_us"],
                "karaka_of": sector_data["karaka_of"],
            })

        # Sort by strength score descending
        sector_signals.sort(key=lambda x: x["strength_score"], reverse=True)

        # Top picks and avoid
        top_sectors = [s for s in sector_signals if s["strength_score"] >= 4]
        avoid_sectors = [s for s in sector_signals if s["strength_score"] <= -4]

        return {
            "date": now.strftime("%Y-%m-%d"),
            "all_signals": sector_signals,
            "top_sectors": top_sectors,
            "avoid_sectors": avoid_sectors,
        }

    def get_ticker_karaka_strength(self, ticker):
        """
        For a specific stock, find which planet rules its sector
        and return that planet's current strength.
        """
        ticker = ticker.upper()

        matching_planets = []
        for planet, sector_data in PLANET_SECTOR_MAP.items():
            all_tickers = sector_data["tickers_india"] + sector_data["tickers_us"]
            if ticker in all_tickers:
                matching_planets.append(planet)

        if not matching_planets:
            return {"karaka_planet": None, "message": "Ticker not mapped to any sector karaka"}

        now = datetime.now()
        positions = self.eph.get_planetary_positions(now)

        results = []
        for planet in matching_planets:
            if planet in positions:
                pos = positions[planet]
                bala = self.bphs.calculate_graha_bala(
                    planet, pos["sign"], pos["degree"], positions
                )
                results.append({
                    "planet": planet,
                    "status": bala["status"],
                    "sign": pos["sign"],
                    "retrograde": pos.get("retrograde", False),
                })

        return {"ticker": ticker, "karaka_planets": results}
