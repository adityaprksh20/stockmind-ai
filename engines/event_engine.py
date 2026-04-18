"""
Event Engine
============
Tracks specific astronomical events that Jyotish considers significant:
- Mercury Retrograde periods
- Eclipses (Solar/Lunar)
- Major conjunctions
- Planetary war (Graha Yuddha)
- Sign ingress (planet changing sign)

Each event is testable: "Does the market behave differently during these events?"
"""

from datetime import datetime, timedelta
from engines.ephemeris_engine import EphemerisEngine


# Known Mercury Retrograde periods (pre-calculated for accuracy)
# Format: (start_date, end_date)
MERCURY_RETRO_2024_2026 = [
    ("2024-04-01", "2024-04-25"),
    ("2024-08-05", "2024-08-28"),
    ("2024-11-25", "2024-12-15"),
    ("2025-03-15", "2025-04-07"),
    ("2025-07-18", "2025-08-11"),
    ("2025-11-09", "2025-11-29"),
    ("2026-02-26", "2026-03-20"),
    ("2026-07-01", "2026-07-25"),
    ("2026-10-24", "2026-11-13"),
]

# Known Eclipse dates
ECLIPSES_2024_2026 = [
    {"date": "2024-03-25", "type": "Lunar", "sign": "Virgo"},
    {"date": "2024-04-08", "type": "Solar", "sign": "Pisces"},
    {"date": "2024-09-18", "type": "Lunar", "sign": "Pisces"},
    {"date": "2024-10-02", "type": "Solar", "sign": "Virgo"},
    {"date": "2025-03-14", "type": "Lunar", "sign": "Virgo"},
    {"date": "2025-03-29", "type": "Solar", "sign": "Pisces"},
    {"date": "2025-09-07", "type": "Lunar", "sign": "Pisces"},
    {"date": "2025-09-21", "type": "Solar", "sign": "Virgo"},
    {"date": "2026-02-17", "type": "Solar", "sign": "Aquarius"},
    {"date": "2026-03-03", "type": "Lunar", "sign": "Virgo"},
    {"date": "2026-08-12", "type": "Solar", "sign": "Leo"},
    {"date": "2026-08-28", "type": "Lunar", "sign": "Aquarius"},
]


class EventEngine:
    """Detect and score current/upcoming Jyotish events."""

    def __init__(self):
        self.eph = EphemerisEngine()

    def is_mercury_retrograde(self, date=None):
        """Check if Mercury is retrograde on given date."""
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        for start, end in MERCURY_RETRO_2024_2026:
            if start <= date_str <= end:
                return {
                    "active": True,
                    "start": start,
                    "end": end,
                    "impact": "Communication/tech disruptions, contract delays, market indecision",
                    "market_effect": -3,
                }

        # Find next retrograde
        for start, end in MERCURY_RETRO_2024_2026:
            if start > date_str:
                return {
                    "active": False,
                    "next_start": start,
                    "next_end": end,
                    "market_effect": 0,
                }

        return {"active": False, "market_effect": 0}

    def get_nearby_eclipses(self, date=None, window_days=15):
        """Get eclipses within window_days of given date."""
        if date is None:
            date = datetime.now()

        nearby = []
        for eclipse in ECLIPSES_2024_2026:
            ecl_date = datetime.strptime(eclipse["date"], "%Y-%m-%d")
            diff = abs((date - ecl_date).days)
            if diff <= window_days:
                # Eclipse impact: strongest within 3 days, fades over 15 days
                if diff <= 3:
                    intensity = "HIGH"
                    market_effect = -5
                elif diff <= 7:
                    intensity = "MEDIUM"
                    market_effect = -3
                else:
                    intensity = "LOW"
                    market_effect = -1

                nearby.append({
                    "date": eclipse["date"],
                    "type": eclipse["type"],
                    "sign": eclipse["sign"],
                    "days_away": diff,
                    "intensity": intensity,
                    "market_effect": market_effect,
                    "interpretation": eclipse["type"] + " eclipse in " + eclipse["sign"] + " - volatility and reversals likely",
                })

        return nearby

    def detect_conjunctions(self, positions):
        """
        Detect when two planets are within 5 degrees in same sign.
        Major conjunctions have significant market impact.
        """
        conjunctions = []
        planets = list(positions.keys())

        for i in range(len(planets)):
            for k in range(i + 1, len(planets)):
                p1, p2 = planets[i], planets[k]
                d1, d2 = positions[p1], positions[p2]

                if d1.get("sign") == d2.get("sign"):
                    deg_diff = abs(d1.get("degree", 0) - d2.get("degree", 0))
                    if deg_diff < 8:
                        # Score conjunction
                        impact = 0
                        interpretation = ""

                        tight = deg_diff < 3

                        # Jupiter + Venus = great benefic conjunction
                        pair = frozenset([p1, p2])
                        if pair == frozenset(["Jupiter", "Venus"]):
                            impact = 8 if tight else 5
                            interpretation = "Jupiter-Venus conjunction - highly auspicious for markets"
                        elif pair == frozenset(["Jupiter", "Mercury"]):
                            impact = 6 if tight else 3
                            interpretation = "Jupiter-Mercury - favorable for finance and IT"
                        elif pair == frozenset(["Saturn", "Mars"]):
                            impact = -8 if tight else -5
                            interpretation = "Saturn-Mars conjunction - conflict, market stress"
                        elif pair == frozenset(["Saturn", "Rahu"]):
                            impact = -7 if tight else -4
                            interpretation = "Saturn-Rahu - fear, systemic risk"
                        elif pair == frozenset(["Jupiter", "Saturn"]):
                            impact = 3 if tight else 1
                            interpretation = "Jupiter-Saturn - major cycle shift (20yr cycle)"
                        elif pair == frozenset(["Sun", "Rahu"]):
                            impact = -4 if tight else -2
                            interpretation = "Sun-Rahu (Grahan Yoga) - leadership crisis"
                        elif pair == frozenset(["Moon", "Rahu"]):
                            impact = -5 if tight else -3
                            interpretation = "Moon-Rahu (Grahan Yoga) - public panic"
                        elif pair == frozenset(["Venus", "Mars"]):
                            impact = 3 if tight else 1
                            interpretation = "Venus-Mars - consumer spending, luxury demand"
                        else:
                            impact = 1 if tight else 0
                            interpretation = p1 + "-" + p2 + " conjunction in " + d1.get("sign", "")

                        if abs(impact) > 0:
                            conjunctions.append({
                                "planet1": p1,
                                "planet2": p2,
                                "sign": d1.get("sign", ""),
                                "degree_diff": round(deg_diff, 1),
                                "tight": tight,
                                "impact": impact,
                                "interpretation": interpretation,
                            })

        conjunctions.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return conjunctions

    def get_all_active_events(self):
        """Get all currently active Jyotish events and their combined impact."""
        now = datetime.now()
        positions = self.eph.get_planetary_positions(now)

        # Mercury retrograde
        merc_retro = self.is_mercury_retrograde(now)

        # Eclipses
        eclipses = self.get_nearby_eclipses(now)

        # Conjunctions
        conjunctions = self.detect_conjunctions(positions)

        # Retrograde count (all planets)
        retrogrades = []
        for planet, data in positions.items():
            if data.get("retrograde") and planet not in ["Rahu", "Ketu"]:
                effect = -2
                if planet == "Mercury":
                    effect = -3
                elif planet == "Jupiter":
                    effect = -4
                elif planet == "Saturn":
                    effect = -2  # Saturn retro is common, less impact
                elif planet == "Venus":
                    effect = -3

                retrogrades.append({
                    "planet": planet,
                    "sign": data.get("sign", ""),
                    "market_effect": effect,
                })

        # Total event impact
        total_impact = 0
        total_impact += merc_retro.get("market_effect", 0)
        total_impact += sum(e.get("market_effect", 0) for e in eclipses)
        total_impact += sum(c.get("impact", 0) for c in conjunctions)
        total_impact += sum(r.get("market_effect", 0) for r in retrogrades)

        # Normalize to 0-100
        event_score = max(0, min(100, 50 + total_impact * 2))

        event_signal = (
            "VERY_FAVORABLE" if event_score >= 70 else
            "FAVORABLE" if event_score >= 58 else
            "NEUTRAL" if event_score >= 42 else
            "CAUTION" if event_score >= 28 else
            "HIGH_RISK"
        )

        return {
            "date": now.strftime("%Y-%m-%d"),
            "event_score": round(event_score, 1),
            "event_signal": event_signal,
            "total_impact": total_impact,
            "mercury_retrograde": merc_retro,
            "eclipses": eclipses,
            "conjunctions": conjunctions,
            "retrogrades": retrogrades,
            "event_count": (
                (1 if merc_retro.get("active") else 0) +
                len(eclipses) + len(conjunctions) + len(retrogrades)
            ),
        }
