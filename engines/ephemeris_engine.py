"""
Vedic Astrology Ephemeris Engine
Pure Python - No C compilation needed
"""

from datetime import datetime

try:
    from kerykeion import AstrologicalSubject
    HAS_KERYKEION = True
except ImportError:
    HAS_KERYKEION = False


class EphemerisEngine:
    """Calculate planetary positions for Vedic Astrology"""

    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini",
        "Mrigashira", "Ardra", "Punarvasu", "Pushya",
        "Ashlesha", "Magha", "Purva Phalguni",
        "Uttara Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]

    AYANAMSHA_2024 = 24.17

    def __init__(self):
        if HAS_KERYKEION:
            print("Using Kerykeion for calculations")
        else:
            print("Using approximate calculations")

    def get_planetary_positions(self, date=None):
        """Get planetary positions in sidereal zodiac"""
        if not date:
            date = datetime.now()

        if HAS_KERYKEION:
            return self._kerykeion_positions(date)
        else:
            return self._approximate_positions(date)

    def _kerykeion_positions(self, date):
        """Positions via Kerykeion"""
        try:
            subject = AstrologicalSubject(
                "Market",
                date.year, date.month, date.day,
                date.hour, date.minute,
                city="Delhi",
                nation="IN"
            )
        except Exception:
            try:
                subject = AstrologicalSubject(
                    "Market",
                    date.year, date.month, date.day,
                    date.hour, date.minute,
                    lng=77.2090, lat=28.6139,
                    tz_str="Asia/Kolkata"
                )
            except Exception:
                return self._approximate_positions(date)

        attrs = {
            "Sun": "sun",
            "Moon": "moon",
            "Mars": "mars",
            "Mercury": "mercury",
            "Jupiter": "jupiter",
            "Venus": "venus",
            "Saturn": "saturn",
        }

        positions = {}

        for name, attr in attrs.items():
            try:
                planet = getattr(subject, attr)
                tropical = planet.abs_pos
                sidereal = (tropical - self.AYANAMSHA_2024) % 360
                sign_num = int(sidereal / 30)
                degree = sidereal % 30
                nak_num = int(sidereal / (360 / 27)) % 27

                positions[name] = {
                    "longitude": round(sidereal, 2),
                    "sign": self.SIGNS[sign_num],
                    "degree": round(degree, 2),
                    "nakshatra": self.NAKSHATRAS[nak_num],
                    "retrograde": getattr(
                        planet, 'retrograde', False
                    )
                }
            except Exception:
                positions[name] = {
                    "longitude": 0,
                    "sign": "Unknown",
                    "degree": 0,
                    "nakshatra": "Unknown",
                    "retrograde": False
                }

        # Rahu
        try:
            rahu_trop = subject.mean_node.abs_pos
            rahu_sid = (rahu_trop - self.AYANAMSHA_2024) % 360
        except Exception:
            rahu_sid = self._calc_rahu(date)

        positions["Rahu"] = {
            "longitude": round(rahu_sid, 2),
            "sign": self.SIGNS[int(rahu_sid / 30)],
            "degree": round(rahu_sid % 30, 2),
            "nakshatra": self.NAKSHATRAS[
                int(rahu_sid / (360 / 27)) % 27
            ],
            "retrograde": True
        }

        ketu_sid = (rahu_sid + 180) % 360
        positions["Ketu"] = {
            "longitude": round(ketu_sid, 2),
            "sign": self.SIGNS[int(ketu_sid / 30)],
            "degree": round(ketu_sid % 30, 2),
            "nakshatra": self.NAKSHATRAS[
                int(ketu_sid / (360 / 27)) % 27
            ],
            "retrograde": True
        }

        return positions

    def _approximate_positions(self, date):
        """Fallback approximate calculations"""
        j2000 = datetime(2000, 1, 1, 12, 0, 0)
        days = (date - j2000).total_seconds() / 86400.0

        orbits = {
            "Sun": (280.46, 0.9856),
            "Moon": (218.32, 13.1764),
            "Mars": (355.45, 0.5240),
            "Mercury": (252.25, 4.0923),
            "Jupiter": (34.40, 0.0831),
            "Venus": (181.98, 1.6021),
            "Saturn": (50.08, 0.0335),
        }

        positions = {}

        for name, (base, daily) in orbits.items():
            tropical = (base + daily * days) % 360
            sidereal = (tropical - self.AYANAMSHA_2024) % 360
            sign_num = int(sidereal / 30)
            nak_num = int(sidereal / (360 / 27)) % 27

            positions[name] = {
                "longitude": round(sidereal, 2),
                "sign": self.SIGNS[sign_num],
                "degree": round(sidereal % 30, 2),
                "nakshatra": self.NAKSHATRAS[nak_num],
                "retrograde": False,
                "accuracy": "approximate"
            }

        rahu_sid = self._calc_rahu(date)
        positions["Rahu"] = {
            "longitude": round(rahu_sid, 2),
            "sign": self.SIGNS[int(rahu_sid / 30)],
            "degree": round(rahu_sid % 30, 2),
            "nakshatra": self.NAKSHATRAS[
                int(rahu_sid / (360 / 27)) % 27
            ],
            "retrograde": True
        }

        ketu_sid = (rahu_sid + 180) % 360
        positions["Ketu"] = {
            "longitude": round(ketu_sid, 2),
            "sign": self.SIGNS[int(ketu_sid / 30)],
            "degree": round(ketu_sid % 30, 2),
            "nakshatra": self.NAKSHATRAS[
                int(ketu_sid / (360 / 27)) % 27
            ],
            "retrograde": True
        }

        return positions

    def _calc_rahu(self, date):
        """Calculate Rahu longitude"""
        j2000 = datetime(2000, 1, 1, 12, 0, 0)
        days = (date - j2000).total_seconds() / 86400.0
        tropical = (125.04 + (-0.0529) * days) % 360
        return (tropical - self.AYANAMSHA_2024) % 360

    def detect_yogas(self, positions):
        """Detect market-relevant planetary yogas"""
        yogas = []
        planets = list(positions.keys())

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]

                if positions[p1]["sign"] == "Unknown":
                    continue
                if positions[p2]["sign"] == "Unknown":
                    continue

                # Conjunction
                if positions[p1]["sign"] == positions[p2]["sign"]:
                    yogas.append({
                        "type": "Conjunction",
                        "planets": p1 + "-" + p2,
                        "sign": positions[p1]["sign"],
                        "significance": self._conjunction_meaning(
                            p1, p2
                        ),
                        "strength": "STRONG"
                    })

                # Opposition
                s1 = self.SIGNS.index(positions[p1]["sign"])
                s2 = self.SIGNS.index(positions[p2]["sign"])
                diff = abs(s1 - s2)

                if diff == 6:
                    yogas.append({
                        "type": "Opposition",
                        "planets": p1 + "-" + p2,
                        "sign": (
                            positions[p1]["sign"] + "-" +
                            positions[p2]["sign"]
                        ),
                        "significance": (
                            p1 + "-" + p2 +
                            " tension: volatility expected"
                        ),
                        "strength": "MODERATE"
                    })

                # Trine
                if diff == 4 or diff == 8:
                    yogas.append({
                        "type": "Trine",
                        "planets": p1 + "-" + p2,
                        "sign": (
                            positions[p1]["sign"] + "-" +
                            positions[p2]["sign"]
                        ),
                        "significance": (
                            p1 + "-" + p2 +
                            " harmony: supportive conditions"
                        ),
                        "strength": "POSITIVE"
                    })

        # Retrograde check
        for planet, data in positions.items():
            if planet in ["Rahu", "Ketu"]:
                continue
            if data.get("retrograde"):
                sector = self._planet_sector(planet)
                yogas.append({
                    "type": "Retrograde",
                    "planets": planet,
                    "sign": data["sign"],
                    "significance": (
                        planet + " retrograde: reversal in " +
                        sector
                    ),
                    "strength": "CAUTION"
                })

        return yogas

    def _conjunction_meaning(self, p1, p2):
        """Market meaning of conjunction"""
        meanings = {
            frozenset(["Jupiter", "Rahu"]):
                "Guru-Chandal: manipulation risk",
            frozenset(["Sun", "Mercury"]):
                "Budh-Aditya: IT sector strong",
            frozenset(["Saturn", "Rahu"]):
                "Shani-Rahu: major disruption",
            frozenset(["Jupiter", "Moon"]):
                "Gajakesari: bull market signal",
            frozenset(["Venus", "Jupiter"]):
                "Wealth yoga: market expansion",
            frozenset(["Mars", "Saturn"]):
                "Conflict: geopolitical tension",
        }
        key = frozenset([p1, p2])
        default = p1 + "-" + p2 + " conjunction: mixed effects"
        return meanings.get(key, default)

    def _planet_sector(self, planet):
        """Sector ruled by planet"""
        sectors = {
            "Sun": "Government/PSU/Gold",
            "Moon": "FMCG/Agriculture",
            "Mars": "Real Estate/Defense",
            "Mercury": "IT/Banking",
            "Jupiter": "Finance/Education",
            "Venus": "Auto/Luxury",
            "Saturn": "Oil/Infrastructure",
            "Rahu": "Tech/Crypto",
            "Ketu": "Pharma/Chemicals"
        }
        return sectors.get(planet, "General")

    def get_market_report(self, date=None):
        """Complete market astrology report"""
        if not date:
            date = datetime.now()

        positions = self.get_planetary_positions(date)
        yogas = self.detect_yogas(positions)

        positive = 0
        negative = 0

        for y in yogas:
            sig = y.get("significance", "").lower()
            strength = y.get("strength", "")

            if "bull" in sig or "expansion" in sig:
                positive += 1
            if strength == "POSITIVE":
                positive += 1
            if "fear" in sig or "tension" in sig:
                negative += 1
            if "disruption" in sig or "manipulation" in sig:
                negative += 1
            if strength == "CAUTION":
                negative += 1

        if positive > negative:
            mood = "BULLISH"
        elif negative > positive:
            mood = "BEARISH"
        else:
            mood = "NEUTRAL"

        return {
            "date": date.strftime("%Y-%m-%d %H:%M"),
            "planetary_positions": positions,
            "active_yogas": yogas,
            "market_mood": mood,
            "positive_signals": positive,
            "negative_signals": negative
        }


if __name__ == "__main__":
    engine = EphemerisEngine()
    positions = engine.get_planetary_positions()

    print("Planetary Positions:")
    for planet, data in positions.items():
        retro = " R" if data.get("retrograde") else ""
        print(
            "  " + planet + ": " +
            data["sign"] + " " +
            str(data["degree"]) + " " +
            data["nakshatra"] + retro
        )

    report = engine.get_market_report()
    print("Market Mood: " + report["market_mood"])