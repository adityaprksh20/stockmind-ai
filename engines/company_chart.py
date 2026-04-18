"""
Company Birth Chart Engine
==========================
Every company has an incorporation date (birth moment).
In Jyotish, this is the company's Kundali.
Planetary transits over this natal chart create company-specific predictions.

This is what makes our system UNIQUE:
- Not generic "Jupiter is bullish"
- Instead: "Jupiter transits company's 11th house (gains) in March"
"""

from datetime import datetime
from engines.ephemeris_engine import EphemerisEngine


# ── COMPANY INCORPORATION DATABASE ──────────────────────
# Source: Public records, MCA filings, SEC filings
# Each entry: ticker -> { date, time (if known), city }
COMPANY_DATABASE = {
    # Indian Blue Chips
    "RELIANCE.NS": {"date": "1973-05-08", "city": "Mumbai", "name": "Reliance Industries"},
    "TCS.NS": {"date": "1968-04-01", "city": "Mumbai", "name": "Tata Consultancy Services"},
    "HDFCBANK.NS": {"date": "1994-08-01", "city": "Mumbai", "name": "HDFC Bank"},
    "INFY.NS": {"date": "1981-07-02", "city": "Pune", "name": "Infosys"},
    "ITC.NS": {"date": "1910-08-24", "city": "Kolkata", "name": "ITC Limited"},
    "WIPRO.NS": {"date": "1945-12-29", "city": "Mumbai", "name": "Wipro"},
    "BHARTIARTL.NS": {"date": "1995-07-07", "city": "New Delhi", "name": "Bharti Airtel"},
    "SBIN.NS": {"date": "1955-07-01", "city": "Mumbai", "name": "State Bank of India"},
    "ICICIBANK.NS": {"date": "1994-01-05", "city": "Mumbai", "name": "ICICI Bank"},
    "KOTAKBANK.NS": {"date": "1985-11-21", "city": "Mumbai", "name": "Kotak Mahindra Bank"},
    "LT.NS": {"date": "1946-02-07", "city": "Mumbai", "name": "Larsen & Toubro"},
    "HINDUNILVR.NS": {"date": "1933-10-17", "city": "Mumbai", "name": "Hindustan Unilever"},
    "BAJFINANCE.NS": {"date": "1987-04-25", "city": "Pune", "name": "Bajaj Finance"},
    "MARUTI.NS": {"date": "1981-02-24", "city": "New Delhi", "name": "Maruti Suzuki"},
    "TATAMOTORS.NS": {"date": "1945-09-01", "city": "Mumbai", "name": "Tata Motors"},
    "SUNPHARMA.NS": {"date": "1983-12-05", "city": "Mumbai", "name": "Sun Pharma"},
    "ADANIENT.NS": {"date": "1993-07-01", "city": "Ahmedabad", "name": "Adani Enterprises"},
    "ASIANPAINT.NS": {"date": "1942-02-01", "city": "Mumbai", "name": "Asian Paints"},
    "TITAN.NS": {"date": "1984-07-25", "city": "Bangalore", "name": "Titan Company"},
    "HCLTECH.NS": {"date": "1991-11-12", "city": "Noida", "name": "HCL Technologies"},

    # US Large Caps
    "AAPL": {"date": "1976-04-01", "city": "Cupertino", "name": "Apple Inc"},
    "MSFT": {"date": "1975-04-04", "city": "Albuquerque", "name": "Microsoft"},
    "GOOGL": {"date": "1998-09-04", "city": "Menlo Park", "name": "Alphabet"},
    "AMZN": {"date": "1994-07-05", "city": "Bellevue", "name": "Amazon"},
    "TSLA": {"date": "2003-07-01", "city": "San Carlos", "name": "Tesla"},
    "NVDA": {"date": "1993-01-01", "city": "Sunnyvale", "name": "NVIDIA"},
    "META": {"date": "2004-02-04", "city": "Cambridge", "name": "Meta Platforms"},
    "JPM": {"date": "1799-11-02", "city": "New York", "name": "JPMorgan Chase"},
    "V": {"date": "1958-09-18", "city": "San Francisco", "name": "Visa Inc"},
    "JNJ": {"date": "1886-01-01", "city": "New Brunswick", "name": "Johnson & Johnson"},
    "WMT": {"date": "1962-07-02", "city": "Rogers", "name": "Walmart"},
    "DIS": {"date": "1923-10-16", "city": "Los Angeles", "name": "Walt Disney"},
    "NFLX": {"date": "1997-08-29", "city": "Scotts Valley", "name": "Netflix"},
    "AMD": {"date": "1969-05-01", "city": "Sunnyvale", "name": "AMD"},
    "INTC": {"date": "1968-07-18", "city": "Mountain View", "name": "Intel"},

    # Global
    "TSM": {"date": "1987-02-21", "city": "Hsinchu", "name": "TSMC"},
    "ASML.AS": {"date": "1984-04-01", "city": "Veldhoven", "name": "ASML"},
    "SAP.DE": {"date": "1972-04-01", "city": "Weinheim", "name": "SAP SE"},
    "SHOP.TO": {"date": "2004-09-01", "city": "Ottawa", "name": "Shopify"},
    "NESN.SW": {"date": "1866-01-01", "city": "Vevey", "name": "Nestle"},
}

# ── ZODIAC SYSTEM ───────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# House meanings in financial context
HOUSE_FINANCE_MEANING = {
    1: {"area": "Company Identity", "effect": "Brand strength, leadership changes"},
    2: {"area": "Revenue & Cash", "effect": "Earnings, cash flow, valuations"},
    3: {"area": "Communications", "effect": "Marketing, partnerships, short-term moves"},
    4: {"area": "Assets & Property", "effect": "Real estate, fixed assets, domestic market"},
    5: {"area": "Speculation & Creativity", "effect": "New products, R&D, speculative gains"},
    6: {"area": "Competition & Debt", "effect": "Competitors, legal issues, operational costs"},
    7: {"area": "Partnerships", "effect": "M&A, JVs, major contracts"},
    8: {"area": "Transformation", "effect": "Restructuring, hidden risks, sudden events"},
    9: {"area": "Expansion", "effect": "International growth, new markets, luck"},
    10: {"area": "Reputation & Status", "effect": "Market position, regulatory, CEO actions"},
    11: {"area": "Gains & Network", "effect": "Profits, institutional support, stock gains"},
    12: {"area": "Losses & Expenses", "effect": "Hidden costs, writedowns, foreign operations"},
}


class CompanyChartEngine:
    """Calculate and analyze company birth charts."""

    def __init__(self):
        self.eph = EphemerisEngine()

    def get_company_info(self, ticker):
        """Get company incorporation data."""
        ticker = ticker.upper()
        if ticker in COMPANY_DATABASE:
            return COMPANY_DATABASE[ticker]
        return None

    def get_natal_chart(self, ticker):
        """
        Calculate the natal (birth) chart for a company.
        This is the company's permanent Kundali.
        """
        company = self.get_company_info(ticker)
        if not company:
            return {"error": "Company not in database. Add incorporation date to use this feature.", "ticker": ticker}

        birth_date = datetime.strptime(company["date"], "%Y-%m-%d")
        natal_positions = self.eph.get_planetary_positions(birth_date)

        # Calculate Lagna (Ascendant sign) - simplified using Sun sign
        # In full implementation, this would use birth time + location
        sun_sign = natal_positions.get("Sun", {}).get("sign", "Aries")
        lagna_sign = sun_sign  # Simplified - uses Sun sign as proxy

        lagna_index = SIGNS.index(lagna_sign) if lagna_sign in SIGNS else 0

        # Calculate house positions for each planet
        natal_houses = {}
        for planet, data in natal_positions.items():
            planet_sign = data.get("sign", "Aries")
            if planet_sign in SIGNS:
                planet_sign_idx = SIGNS.index(planet_sign)
                house = ((planet_sign_idx - lagna_index) % 12) + 1
            else:
                house = 1
            natal_houses[planet] = {
                "sign": planet_sign,
                "degree": data.get("degree", 0),
                "house": house,
                "house_meaning": HOUSE_FINANCE_MEANING.get(house, {}),
                "retrograde": data.get("retrograde", False),
            }

        return {
            "ticker": ticker,
            "name": company["name"],
            "birth_date": company["date"],
            "city": company["city"],
            "lagna_sign": lagna_sign,
            "natal_positions": natal_houses,
        }

    def get_current_transits_over_natal(self, ticker):
        """
        THE KEY FUNCTION: Current planetary transits over company birth chart.

        This creates company-SPECIFIC predictions:
        - Jupiter transiting company's 11th house = gains period
        - Saturn transiting company's 8th house = transformation/risk
        - Rahu over natal Sun = sudden leadership changes
        """
        natal = self.get_natal_chart(ticker)
        if "error" in natal:
            return natal

        now = datetime.now()
        current_positions = self.eph.get_planetary_positions(now)

        lagna_sign = natal["lagna_sign"]
        lagna_index = SIGNS.index(lagna_sign) if lagna_sign in SIGNS else 0

        transits = []
        transit_score = 0  # -50 to +50

        for planet, data in current_positions.items():
            planet_sign = data.get("sign", "Aries")
            if planet_sign in SIGNS:
                planet_sign_idx = SIGNS.index(planet_sign)
                transit_house = ((planet_sign_idx - lagna_index) % 12) + 1
            else:
                transit_house = 1

            house_info = HOUSE_FINANCE_MEANING.get(transit_house, {})

            # Score the transit
            impact = 0
            interpretation = ""

            # ── JUPITER TRANSITS (most important for wealth) ──
            if planet == "Jupiter":
                if transit_house in [1, 5, 9]:  # Trikona
                    impact = 8
                    interpretation = "Jupiter in trikona - strong growth period"
                elif transit_house in [2, 11]:  # Wealth houses
                    impact = 10
                    interpretation = "Jupiter in wealth house - revenue & stock gains"
                elif transit_house in [7, 10]:  # Kendra
                    impact = 6
                    interpretation = "Jupiter in kendra - stability and partnerships"
                elif transit_house in [6, 8, 12]:  # Dusthana
                    impact = -6
                    interpretation = "Jupiter in dusthana - challenges, hidden costs"
                elif transit_house == 4:
                    impact = 4
                    interpretation = "Jupiter over assets - property/infrastructure growth"

            # ── SATURN TRANSITS (discipline or restriction) ──
            elif planet == "Saturn":
                if transit_house in [3, 6, 11]:  # Saturn does well
                    impact = 5
                    interpretation = "Saturn well-placed - disciplined growth"
                elif transit_house in [1, 4, 7, 10]:  # Sade-sati like
                    impact = -5
                    interpretation = "Saturn in kendra - pressure, restructuring"
                elif transit_house == 8:
                    impact = -8
                    interpretation = "Saturn in 8th - major transformation, risk"
                elif transit_house == 12:
                    impact = -6
                    interpretation = "Saturn in 12th - hidden expenses, foreign losses"
                elif transit_house in [2, 5, 9]:
                    impact = -3
                    interpretation = "Saturn restricting growth houses"

            # ── RAHU TRANSITS (sudden, amplifying) ──
            elif planet == "Rahu":
                if transit_house in [3, 6, 11]:
                    impact = 6
                    interpretation = "Rahu amplifying gains - unconventional growth"
                elif transit_house in [1, 5, 9]:
                    impact = -3
                    interpretation = "Rahu creating illusion - verify fundamentals"
                elif transit_house == 10:
                    impact = 4
                    interpretation = "Rahu in 10th - sudden fame/notoriety"
                elif transit_house in [8, 12]:
                    impact = -7
                    interpretation = "Rahu in dusthana - hidden risks, fraud potential"

            # ── KETU TRANSITS (detachment, spirituality) ──
            elif planet == "Ketu":
                if transit_house in [6, 8, 12]:
                    impact = 3
                    interpretation = "Ketu reducing obstacles"
                elif transit_house in [2, 11]:
                    impact = -5
                    interpretation = "Ketu detaching from wealth - profit concerns"
                elif transit_house == 1:
                    impact = -4
                    interpretation = "Ketu on lagna - identity crisis, rebranding"

            # ── MARS TRANSITS (energy, aggression) ──
            elif planet == "Mars":
                if transit_house in [3, 6, 10, 11]:
                    impact = 4
                    interpretation = "Mars energizing action houses - competitive edge"
                elif transit_house in [1, 4, 7, 8]:
                    impact = -3
                    interpretation = "Mars creating friction - conflicts, impulsive decisions"

            # ── VENUS TRANSITS (luxury, finance) ──
            elif planet == "Venus":
                if transit_house in [1, 2, 4, 5, 7, 9, 11]:
                    impact = 3
                    interpretation = "Venus favorable - consumer sentiment, luxury demand"
                elif transit_house in [6, 8, 12]:
                    impact = -2
                    interpretation = "Venus weak - consumer spending concerns"

            # ── MERCURY TRANSITS (business, communication) ──
            elif planet == "Mercury":
                if transit_house in [1, 2, 5, 7, 10, 11]:
                    impact = 3
                    interpretation = "Mercury favorable - deals, communications, IT"
                elif transit_house in [6, 8, 12]:
                    impact = -2
                    interpretation = "Mercury weak - miscommunication, contract issues"
                if data.get("retrograde"):
                    impact -= 3
                    interpretation += " [RETROGRADE: delays, review needed]"

            # ── MOON TRANSIT (sentiment, daily mood) ──
            elif planet == "Moon":
                if transit_house in [1, 4, 7, 10]:
                    impact = 2
                    interpretation = "Moon in kendra - stable sentiment"
                elif transit_house in [6, 8, 12]:
                    impact = -2
                    interpretation = "Moon in dusthana - negative sentiment today"

            # ── SUN TRANSIT (authority, government) ──
            elif planet == "Sun":
                if transit_house in [1, 5, 9, 10, 11]:
                    impact = 3
                    interpretation = "Sun strong - government favor, leadership clarity"
                elif transit_house in [6, 8, 12]:
                    impact = -2
                    interpretation = "Sun weak - regulatory pressure"

            # Check if transit planet is near natal planet (conjunction)
            natal_planet_data = natal["natal_positions"].get(planet, {})
            natal_degree = natal_planet_data.get("degree", -999)
            transit_degree = data.get("degree", 0)
            if natal_planet_data.get("sign") == planet_sign:
                degree_diff = abs(transit_degree - natal_degree)
                if degree_diff < 5:  # Tight conjunction with natal position
                    impact = int(impact * 1.5)
                    interpretation += " [RETURN to natal position - significant]"

            transit_score += impact

            transits.append({
                "planet": planet,
                "sign": planet_sign,
                "degree": round(data.get("degree", 0), 1),
                "retrograde": data.get("retrograde", False),
                "transit_house": transit_house,
                "house_area": house_info.get("area", ""),
                "house_effect": house_info.get("effect", ""),
                "impact": impact,
                "interpretation": interpretation,
            })

        # Sort by absolute impact
        transits.sort(key=lambda x: abs(x["impact"]), reverse=True)

        # Convert transit_score to 0-100
        normalized_score = max(0, min(100, 50 + transit_score))

        transit_signal = (
            "STRONG_BUY" if normalized_score >= 72 else
            "BUY" if normalized_score >= 58 else
            "NEUTRAL" if normalized_score >= 42 else
            "SELL" if normalized_score >= 28 else
            "STRONG_SELL"
        )

        # Top positive and negative transits
        positive = [t for t in transits if t["impact"] > 0]
        negative = [t for t in transits if t["impact"] < 0]

        return {
            "ticker": natal["ticker"],
            "name": natal["name"],
            "birth_date": natal["birth_date"],
            "lagna": natal["lagna_sign"],
            "transit_score": round(normalized_score, 1),
            "transit_signal": transit_signal,
            "raw_score": transit_score,
            "transits": transits,
            "top_positive": positive[:3],
            "top_negative": negative[:3],
            "positive_count": len(positive),
            "negative_count": len(negative),
        }
