"""
Enhanced Jyotish Agent - BPHS + BNN Combined Analysis
"""

import json
from datetime import datetime
from engines.mamba_engine import get_creative_llm
from engines.ephemeris_engine import EphemerisEngine
from engines.vedic_core import BPHSSystem, BNNSystem


class JyotishAgent:
    """Enhanced Vedic Astrology market predictions using BPHS + BNN"""

    def __init__(self):
        self.llm = get_creative_llm()
        self.ephemeris = EphemerisEngine()
        self.bphs = BPHSSystem()
        self.bnn = BNNSystem()

    def _get_full_vedic_analysis(self):
        """Get complete BPHS + BNN analysis of current sky"""

        positions = self.ephemeris.get_planetary_positions()
        yogas = self.ephemeris.detect_yogas(positions)

        # BPHS Analysis
        graha_balas = {}
        for planet, data in positions.items():
            bala = self.bphs.calculate_graha_bala(
                planet, data["sign"], data["degree"], positions
            )
            avastha = self.bphs.get_graha_avastha(
                planet, data["sign"], data["degree"]
            )
            graha_balas[planet] = {
                "bala": bala,
                "avastha": avastha,
                "sign": data["sign"],
                "degree": data["degree"],
                "nakshatra": data.get("nakshatra", ""),
                "retrograde": data.get("retrograde", False)
            }

        dhana_yogas = self.bphs.detect_dhana_yogas(positions)

        # BNN Analysis
        bnn_score = self.bnn.get_market_nakshatra_score(positions)
        moon_analysis = self.bnn.get_moon_nakshatra_analysis(positions)
        all_nakshatras = self.bnn.get_all_planet_nakshatras(positions)

        return {
            "positions": positions,
            "basic_yogas": yogas,
            "graha_balas": graha_balas,
            "dhana_yogas": dhana_yogas,
            "bnn_score": bnn_score,
            "moon_analysis": moon_analysis,
            "planet_nakshatras": all_nakshatras
        }

    def predict_market_trend(self, date=None):
        """Enhanced market prediction using BPHS + BNN"""

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        analysis = self._get_full_vedic_analysis()

        # Format BPHS data
        bphs_text = "GRAHA BALA (Planetary Strength - BPHS):\n"
        for planet, data in analysis["graha_balas"].items():
            bala = data["bala"]
            avastha = data["avastha"]
            retro = " [RETROGRADE]" if data["retrograde"] else ""
            bphs_text += (
                "  " + planet + " in " + data["sign"] +
                " " + str(data["degree"]) + "° (" + data["nakshatra"] + ")" + retro + "\n"
                "    Strength: " + str(bala["total"]) + " (" + bala["status"] + ")\n"
                "    State: " + avastha["state"] + " (Factor: " + str(avastha["strength_factor"]) + ")\n"
                "    Market: " + avastha["market_effect"] + "\n"
            )
            for detail in bala["details"]:
                bphs_text += "    → " + detail + "\n"

        # Format Dhana Yogas
        dhana_text = "DHANA YOGAS (Wealth Combinations - BPHS Ch.41):\n"
        for yoga in analysis["dhana_yogas"]:
            dhana_text += (
                "  " + yoga["name"] + " [" + yoga["type"] + " - " + yoga["strength"] + "]\n"
                "    Planets: " + yoga["planets"] + "\n"
                "    Effect: " + yoga["effect"] + "\n"
            )
        if not analysis["dhana_yogas"]:
            dhana_text += "  No major dhana yogas active currently.\n"

        # Format BNN data
        bnn_text = "BNN (Nakshatra Analysis):\n"
        bnn_text += "  Overall BNN Score: " + str(analysis["bnn_score"]["bnn_score"]) + "/10\n"

        moon = analysis["moon_analysis"]
        if "error" not in moon:
            bnn_text += (
                "  Moon Nakshatra: " + moon["moon_nakshatra"] +
                " (Lord: " + moon["lord"] + ")\n"
                "  Financial Nature: " + moon["financial_nature"] + "\n"
                "  Market Effect: " + moon["market_effect"] + "\n"
                "  Trading Style: " + moon["trading_style"] + "\n"
                "  Sectors: " + ", ".join(moon["sector_affinity"]) + "\n"
            )

        for detail in analysis["bnn_score"]["details"]:
            bnn_text += "  → " + detail + "\n"

        # Format nakshatra details
        nak_text = "PLANET-NAKSHATRA MAPPING (BNN):\n"
        for planet, data in analysis["planet_nakshatras"].items():
            nak_text += (
                "  " + planet + " in " + data["nakshatra"] +
                " (Lord: " + data["nak_lord"] +
                ", Str: " + str(data["strength"]) + "/10)\n"
                "    " + data["market_effect"] + "\n"
                "    Sectors: " + ", ".join(data["sectors"]) + "\n"
            )

        prompt = (
            "You are a master Vedic Financial Astrologer trained in both "
            "Brihat Parashara Hora Shastra (BPHS) and Brihat Nakshatra Nidhi (BNN).\n\n"
            "Date: " + date + "\n\n"
            "=== BPHS ANALYSIS ===\n" + bphs_text + "\n"
            "=== DHANA YOGAS ===\n" + dhana_text + "\n"
            "=== BNN ANALYSIS ===\n" + bnn_text + "\n"
            "=== NAKSHATRA MAPPING ===\n" + nak_text + "\n"
            "Based on BOTH BPHS and BNN systems, provide:\n\n"
            "### 1. BPHS VERDICT\n"
            "- Strongest planets and what they favor\n"
            "- Weakest planets and what to avoid\n"
            "- Active Dhana/Raja/Dosha Yogas impact\n"
            "- Graha Avastha (planetary states) market effect\n\n"
            "### 2. BNN VERDICT\n"
            "- Moon nakshatra market guidance\n"
            "- Key nakshatra influences today\n"
            "- Nakshatra-based sector recommendations\n"
            "- Best trading style for current nakshatras\n\n"
            "### 3. COMBINED BPHS+BNN PREDICTION\n"
            "- Market direction: BULLISH/BEARISH/NEUTRAL\n"
            "- Confidence level based on both systems agreeing\n"
            "- This week outlook\n"
            "- This month outlook\n\n"
            "### 4. SECTOR RECOMMENDATIONS\n"
            "For each: BUY/HOLD/SELL with BPHS+BNN reasoning\n"
            "- Banking & Finance\n"
            "- IT & Technology\n"
            "- Pharma & Healthcare\n"
            "- Energy & Oil\n"
            "- Auto & Manufacturing\n"
            "- FMCG & Consumer\n"
            "- Real Estate\n"
            "- Metals & Mining\n\n"
            "### 5. TIMING (BNN Muhurat)\n"
            "- Best dates/nakshatras for buying\n"
            "- Nakshatras to avoid trading\n"
            "- Pushya nakshatra dates (most auspicious for investment)\n\n"
            "### 6. RISK FACTORS\n"
            "- Dosha yogas active (warnings)\n"
            "- Retrograde planet effects\n"
            "- Malefic nakshatra periods\n\n"
            "Disclaimer: Jyotish predictions are speculative. Not financial advice.\n"
        )

        return self.llm(prompt)

    def analyze_stock_astrology(self, ticker, listing_date):
        """Stock kundali using BPHS + BNN"""

        analysis = self._get_full_vedic_analysis()

        bphs_summary = ""
        for planet, data in analysis["graha_balas"].items():
            bala = data["bala"]
            if bala["status"] in ["VERY_STRONG", "STRONG", "VERY_WEAK"]:
                bphs_summary += (
                    planet + ": " + bala["status"] +
                    " (" + str(bala["total"]) + ") in " + data["sign"] + "\n"
                )

        dhana_summary = ""
        for yoga in analysis["dhana_yogas"]:
            dhana_summary += yoga["name"] + ": " + yoga["effect"] + "\n"

        moon = analysis["moon_analysis"]
        bnn_summary = ""
        if "error" not in moon:
            bnn_summary = (
                "Moon in " + moon["moon_nakshatra"] +
                " - " + moon["market_effect"] + "\n"
                "BNN Score: " + str(analysis["bnn_score"]["bnn_score"]) + "/10\n"
            )

        prompt = (
            "You are a Vedic Financial Astrologer using BPHS + BNN.\n\n"
            "Stock: " + ticker + "\n"
            "Listing Date: " + listing_date + "\n\n"
            "CURRENT BPHS (Planetary Strength):\n" + bphs_summary + "\n"
            "DHANA YOGAS:\n" + dhana_summary + "\n"
            "BNN (Nakshatra) Analysis:\n" + bnn_summary + "\n"
            "## Provide BPHS + BNN Stock Analysis:\n\n"
            "### 1. LISTING CHART (BPHS)\n"
            "Likely planetary yogas at listing date.\n\n"
            "### 2. CURRENT TRANSIT (BPHS+BNN)\n"
            "How current planetary strength + nakshatras affect this stock.\n\n"
            "### 3. PREDICTION\n"
            "- 1 month outlook with BPHS reasoning\n"
            "- 6 month outlook with BNN nakshatra cycles\n"
            "- 1 year outlook combining both\n\n"
            "### 4. BNN TIMING\n"
            "- Best nakshatras to BUY this stock\n"
            "- Nakshatras to SELL/book profits\n"
            "- Nakshatras to AVOID\n\n"
            "### 5. BPHS YOGA IMPACT\n"
            "Which active yogas specifically help or hurt this stock.\n\n"
            "Disclaimer: Speculative. Not financial advice.\n"
        )

        return self.llm(prompt)

    def world_events_prediction(self):
        """World events using BPHS + BNN"""

        analysis = self._get_full_vedic_analysis()

        # Summarize key findings
        strong_planets = []
        weak_planets = []
        for planet, data in analysis["graha_balas"].items():
            if data["bala"]["status"] in ["VERY_STRONG", "STRONG"]:
                strong_planets.append(planet + " in " + data["sign"])
            elif data["bala"]["status"] in ["VERY_WEAK", "WEAK"]:
                weak_planets.append(planet + " in " + data["sign"])

        dhana_names = [y["name"] + " (" + y["strength"] + ")" for y in analysis["dhana_yogas"]]

        moon = analysis["moon_analysis"]
        moon_text = ""
        if "error" not in moon:
            moon_text = (
                "Moon in " + moon["moon_nakshatra"] +
                " (" + moon["lord"] + "): " + moon["financial_nature"]
            )

        prompt = (
            "You are a Mundane Astrology (Medini Jyotish) expert using BPHS + BNN.\n\n"
            "Date: " + datetime.now().strftime("%Y-%m-%d") + "\n\n"
            "STRONG Planets (BPHS): " + ", ".join(strong_planets) + "\n"
            "WEAK Planets (BPHS): " + ", ".join(weak_planets) + "\n"
            "Active Yogas: " + ", ".join(dhana_names) + "\n"
            "BNN Score: " + str(analysis["bnn_score"]["bnn_score"]) + "/10\n"
            "Moon (BNN): " + moon_text + "\n\n"
            "## MUNDANE PREDICTIONS (BPHS+BNN):\n\n"
            "### 1. GEOPOLITICAL (based on strong/weak planets)\n\n"
            "### 2. ECONOMIC OUTLOOK\n"
            "Using Dhana Yogas and planetary strength.\n\n"
            "### 3. GLOBAL MARKETS\n"
            "India, US, Europe, Asia direction.\n\n"
            "### 4. COMMODITIES\n"
            "Gold (Sun), Silver (Moon), Oil (Saturn), Metals (Mars).\n\n"
            "### 5. NEXT 3 MONTHS (BNN Nakshatra Cycles)\n"
            "Month-by-month based on Moon's nakshatra transit pattern.\n\n"
            "### 6. CRITICAL DATES\n"
            "Based on BNN muhurat and BPHS yoga formations.\n\n"
            "### 7. TOP 3 HIGH-CONVICTION PREDICTIONS\n"
            "With specific BPHS yoga + BNN nakshatra reasoning.\n\n"
            "Disclaimer: Speculative. Not financial advice.\n"
        )

        return self.llm(prompt)

    def get_bphs_bnn_summary(self):
        """Quick summary for dashboard"""
        analysis = self._get_full_vedic_analysis()

        return {
            "bnn_score": analysis["bnn_score"]["bnn_score"],
            "moon_analysis": analysis["moon_analysis"],
            "dhana_yogas": analysis["dhana_yogas"],
            "graha_balas": {
                planet: {
                    "status": data["bala"]["status"],
                    "total": data["bala"]["total"],
                    "avastha": data["avastha"]["state"]
                }
                for planet, data in analysis["graha_balas"].items()
            },
            "planet_nakshatras": analysis["planet_nakshatras"]
        }


if __name__ == "__main__":
    agent = JyotishAgent()
    print("Enhanced Jyotish Agent (BPHS+BNN) loaded OK")

    summary = agent.get_bphs_bnn_summary()
    print("\nBNN Score: " + str(summary["bnn_score"]) + "/10")

    moon = summary["moon_analysis"]
    if "error" not in moon:
        print("Moon: " + moon["moon_nakshatra"] + " - " + moon["financial_nature"])

    print("\nDhana Yogas:")
    for y in summary["dhana_yogas"]:
        print("  " + y["name"] + " [" + y["strength"] + "]: " + y["effect"])

    print("\nGraha Bala:")
    for planet, data in summary["graha_balas"].items():
        print("  " + planet + ": " + data["status"] + " (" + str(data["total"]) + ") - " + data["avastha"])
