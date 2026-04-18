"""
Real-Time Astro Engine
======================
ALL astronomical events calculated in real-time using Swiss Ephemeris.
Nothing hardcoded. Every position, conjunction, retrograde computed live.
"""

import swisseph as swe
from datetime import datetime, timedelta
import math

# Swiss Ephemeris planet IDs
PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Ayanamsa: Lahiri (Chitrapaksha)
swe.set_sid_mode(swe.SIDM_LAHIRI)


def datetime_to_jd(dt):
    """Convert Python datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def get_sidereal_position(planet_id, jd):
    """Get sidereal (Vedic) longitude for a planet."""
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    try:
        result = swe.calc_ut(jd, planet_id, flags)
        longitude = result[0][0]
        speed = result[0][3]
        if longitude < 0:
            longitude += 360
        return longitude, speed
    except Exception:
        return 0.0, 0.0


def longitude_to_sign(lon):
    """Convert longitude to zodiac sign."""
    sign_index = int(lon / 30) % 12
    return SIGNS[sign_index]


def longitude_to_nakshatra(lon):
    """Convert longitude to nakshatra."""
    nak_index = int(lon / (360 / 27)) % 27
    pada = int((lon % (360 / 27)) / (360 / 108)) + 1
    return NAKSHATRAS[nak_index], pada


class RealtimeAstroEngine:
    """All astronomical data computed in real-time."""

    def get_all_positions(self, dt=None):
        """
        Get real-time sidereal positions for all planets.
        No caching, no hardcoding — computed fresh every call.
        """
        if dt is None:
            dt = datetime.utcnow()

        jd = datetime_to_jd(dt)
        positions = {}

        for name, pid in PLANET_IDS.items():
            lon, speed = get_sidereal_position(pid, jd)

            sign = longitude_to_sign(lon)
            degree_in_sign = lon % 30
            nakshatra, pada = longitude_to_nakshatra(lon)

            # Retrograde: negative speed (Rahu/Ketu always retrograde)
            is_retro = speed < 0
            if name == "Rahu":
                is_retro = True  # Rahu always retrograde in mean node

            positions[name] = {
                "longitude": round(lon, 4),
                "sign": sign,
                "degree": round(degree_in_sign, 2),
                "nakshatra": nakshatra,
                "pada": pada,
                "speed": round(speed, 4),
                "retrograde": is_retro,
            }

        # Ketu is always 180 degrees from Rahu
        if "Rahu" in positions:
            ketu_lon = (positions["Rahu"]["longitude"] + 180) % 360
            positions["Ketu"] = {
                "longitude": round(ketu_lon, 4),
                "sign": longitude_to_sign(ketu_lon),
                "degree": round(ketu_lon % 30, 2),
                "nakshatra": longitude_to_nakshatra(ketu_lon)[0],
                "pada": longitude_to_nakshatra(ketu_lon)[1],
                "speed": 0,
                "retrograde": True,
            }

        return positions

    def get_all_conjunctions(self, dt=None, orb=8.0):
        """
        Detect ALL current conjunctions (planets within orb degrees).
        Calculated in real-time.
        """
        positions = self.get_all_positions(dt)
        conjunctions = []
        planets = list(positions.keys())

        for i in range(len(planets)):
            for k in range(i + 1, len(planets)):
                p1, p2 = planets[i], planets[k]
                lon1 = positions[p1]["longitude"]
                lon2 = positions[p2]["longitude"]

                # Angular distance (handles 360/0 wrap)
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff

                if diff <= orb:
                    conjunctions.append({
                        "planet1": p1,
                        "planet2": p2,
                        "sign": positions[p1]["sign"],
                        "degree_separation": round(diff, 2),
                        "tight": diff < 3,
                    })

        return conjunctions

    def get_all_retrogrades(self, dt=None):
        """Get list of currently retrograde planets."""
        positions = self.get_all_positions(dt)
        retrogrades = []

        for name, data in positions.items():
            if name in ["Rahu", "Ketu"]:
                continue
            if data["retrograde"]:
                retrogrades.append({
                    "planet": name,
                    "sign": data["sign"],
                    "degree": data["degree"],
                    "speed": data["speed"],
                })

        return retrogrades

    def detect_eclipses_upcoming(self, days_ahead=60):
        """
        Detect upcoming eclipses by checking Sun-Moon-Rahu/Ketu alignment.
        Solar eclipse: New Moon near Rahu/Ketu (Sun-Moon conjunction near nodes)
        Lunar eclipse: Full Moon near Rahu/Ketu (Sun-Moon opposition near nodes)
        """
        now = datetime.utcnow()
        eclipses = []

        for day_offset in range(days_ahead):
            check_date = now + timedelta(days=day_offset)
            jd = datetime_to_jd(check_date)

            sun_lon, _ = get_sidereal_position(swe.SUN, jd)
            moon_lon, _ = get_sidereal_position(swe.MOON, jd)
            rahu_lon, _ = get_sidereal_position(swe.MEAN_NODE, jd)
            ketu_lon = (rahu_lon + 180) % 360

            # Sun-Moon distance
            sun_moon_diff = abs(sun_lon - moon_lon)
            if sun_moon_diff > 180:
                sun_moon_diff = 360 - sun_moon_diff

            # Distance of Moon from Rahu/Ketu
            moon_rahu = abs(moon_lon - rahu_lon)
            if moon_rahu > 180:
                moon_rahu = 360 - moon_rahu

            moon_ketu = abs(moon_lon - ketu_lon)
            if moon_ketu > 180:
                moon_ketu = 360 - moon_ketu

            node_proximity = min(moon_rahu, moon_ketu)

            # Solar eclipse: New Moon (Sun-Moon < 12 deg) near node (< 18 deg)
            if sun_moon_diff < 12 and node_proximity < 18:
                eclipses.append({
                    "date": check_date.strftime("%Y-%m-%d"),
                    "type": "Solar",
                    "sign": longitude_to_sign(sun_lon),
                    "days_away": day_offset,
                    "sun_moon_sep": round(sun_moon_diff, 1),
                    "node_proximity": round(node_proximity, 1),
                })

            # Lunar eclipse: Full Moon (Sun-Moon ~180 deg) near node
            if abs(sun_moon_diff - 180) < 12 and node_proximity < 18:
                eclipses.append({
                    "date": check_date.strftime("%Y-%m-%d"),
                    "type": "Lunar",
                    "sign": longitude_to_sign(moon_lon),
                    "days_away": day_offset,
                    "sun_moon_sep": round(sun_moon_diff, 1),
                    "node_proximity": round(node_proximity, 1),
                })

        # Deduplicate (eclipses span multiple days)
        seen = set()
        unique = []
        for e in eclipses:
            key = e["type"] + "_" + e["date"][:7]
            if key not in seen:
                seen.add(key)
                unique.append(e)

        return unique

    def get_moon_phase(self, dt=None):
        """Calculate current Moon phase."""
        if dt is None:
            dt = datetime.utcnow()

        jd = datetime_to_jd(dt)
        sun_lon, _ = get_sidereal_position(swe.SUN, jd)
        moon_lon, _ = get_sidereal_position(swe.MOON, jd)

        # Tithi calculation
        diff = (moon_lon - sun_lon) % 360
        tithi_num = int(diff / 12) + 1  # 1-30

        if tithi_num <= 5:
            phase = "Shukla Pratipada-Panchami (Waxing New)"
            market_bias = "cautious"
        elif tithi_num <= 10:
            phase = "Shukla Shashti-Dashami (Waxing Growing)"
            market_bias = "bullish"
        elif tithi_num <= 15:
            phase = "Shukla Ekadashi-Purnima (Near Full Moon)"
            market_bias = "peak optimism"
        elif tithi_num <= 20:
            phase = "Krishna Pratipada-Panchami (Waning Start)"
            market_bias = "distribution"
        elif tithi_num <= 25:
            phase = "Krishna Shashti-Dashami (Waning)"
            market_bias = "bearish"
        else:
            phase = "Krishna Ekadashi-Amavasya (Near New Moon)"
            market_bias = "fear/bottoming"

        return {
            "tithi": tithi_num,
            "phase": phase,
            "market_bias": market_bias,
            "moon_sign": longitude_to_sign(moon_lon),
            "moon_nakshatra": longitude_to_nakshatra(moon_lon)[0],
            "moon_degree": round(moon_lon % 30, 2),
        }

    def get_complete_snapshot(self, dt=None):
        """Single call: get EVERYTHING about current sky."""
        if dt is None:
            dt = datetime.utcnow()

        positions = self.get_all_positions(dt)
        conjunctions = self.get_all_conjunctions(dt)
        retrogrades = self.get_all_retrogrades(dt)
        moon = self.get_moon_phase(dt)
        eclipses = self.detect_eclipses_upcoming()

        return {
            "timestamp": dt.strftime("%Y-%m-%d %H:%M UTC"),
            "positions": positions,
            "conjunctions": conjunctions,
            "retrogrades": retrogrades,
            "retrograde_count": len(retrogrades),
            "moon_phase": moon,
            "upcoming_eclipses": eclipses,
        }
