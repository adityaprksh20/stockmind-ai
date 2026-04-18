"""
Vedic Astrology Core - BPHS + BNN Systems
Implements classical Jyotish calculations for market analysis
"""


class BPHSSystem:
    """
    Brihat Parashara Hora Shastra calculations
    Planetary dignity, strength, and yoga analysis
    """

    # Graha ownership (BPHS Ch.4)
    GRAHA_OWNERSHIP = {
        "Sun": ["Leo"],
        "Moon": ["Cancer"],
        "Mars": ["Aries", "Scorpio"],
        "Mercury": ["Gemini", "Virgo"],
        "Jupiter": ["Sagittarius", "Pisces"],
        "Venus": ["Taurus", "Libra"],
        "Saturn": ["Capricorn", "Aquarius"],
        "Rahu": ["Aquarius"],
        "Ketu": ["Scorpio"]
    }

    # Exaltation signs and degrees (BPHS Ch.3)
    UCCHA = {
        "Sun": {"sign": "Aries", "degree": 10},
        "Moon": {"sign": "Taurus", "degree": 3},
        "Mars": {"sign": "Capricorn", "degree": 28},
        "Mercury": {"sign": "Virgo", "degree": 15},
        "Jupiter": {"sign": "Cancer", "degree": 5},
        "Venus": {"sign": "Pisces", "degree": 27},
        "Saturn": {"sign": "Libra", "degree": 20},
        "Rahu": {"sign": "Taurus", "degree": 20},
        "Ketu": {"sign": "Scorpio", "degree": 20}
    }

    # Debilitation signs (BPHS Ch.3)
    NEECHA = {
        "Sun": {"sign": "Libra", "degree": 10},
        "Moon": {"sign": "Scorpio", "degree": 3},
        "Mars": {"sign": "Cancer", "degree": 28},
        "Mercury": {"sign": "Pisces", "degree": 15},
        "Jupiter": {"sign": "Capricorn", "degree": 5},
        "Venus": {"sign": "Virgo", "degree": 27},
        "Saturn": {"sign": "Aries", "degree": 20},
        "Rahu": {"sign": "Scorpio", "degree": 20},
        "Ketu": {"sign": "Taurus", "degree": 20}
    }

    # Mool Trikona signs (BPHS Ch.3)
    MOOLTRIKONA = {
        "Sun": {"sign": "Leo", "start": 0, "end": 20},
        "Moon": {"sign": "Taurus", "start": 3, "end": 30},
        "Mars": {"sign": "Aries", "start": 0, "end": 12},
        "Mercury": {"sign": "Virgo", "start": 15, "end": 20},
        "Jupiter": {"sign": "Sagittarius", "start": 0, "end": 10},
        "Venus": {"sign": "Libra", "start": 0, "end": 15},
        "Saturn": {"sign": "Aquarius", "start": 0, "end": 20}
    }

    # Natural friendship (BPHS Ch.3)
    NAISARGIKA_MITRA = {
        "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
        "Moon": {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
        "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
        "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
        "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
        "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
        "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]}
    }

    # Karaka (significator) - BPHS
    KARAKA = {
        "Sun": "Authority, Government, Gold, Father",
        "Moon": "Mind, Public, Silver, Mother, Liquids",
        "Mars": "Energy, Land, Metals, Brothers, Military",
        "Mercury": "Intelligence, Trade, Communication, Education",
        "Jupiter": "Wealth, Wisdom, Banking, Children, Expansion",
        "Venus": "Luxury, Vehicles, Art, Spouse, Comfort",
        "Saturn": "Labour, Oil, Mining, Delays, Discipline",
        "Rahu": "Foreign, Technology, Illusion, Unconventional",
        "Ketu": "Spirituality, Detachment, Research, Pharma"
    }

    # Bhava (House) significations for market (BPHS)
    BHAVA_MARKET = {
        1: "Market sentiment, overall direction, new launches",
        2: "Banking, financial assets, currency, national wealth",
        3: "Communication, media, telecom, short travels, IT services",
        4: "Real estate, vehicles, agriculture, domestic happiness",
        5: "Speculation, stock market, entertainment, creativity",
        6: "Debt, healthcare, pharma, competition, enemies",
        7: "Partnerships, foreign trade, international markets",
        8: "Insurance, hidden wealth, sudden gains/losses, transformation",
        9: "Fortune, dharma, international affairs, higher education",
        10: "Government, career, authority, corporate leadership",
        11: "Gains, income, large organizations, networks",
        12: "Losses, foreign lands, expenses, institutions, endings"
    }

    def calculate_graha_bala(self, planet, sign, degree, positions):
        """
        Calculate planetary strength (simplified Shadbala)
        Based on BPHS Ch.27

        Components:
        1. Sthana Bala (Positional strength)
        2. Dig Bala (Directional strength)
        3. Kala Bala (Temporal strength) - simplified
        4. Naisargika Bala (Natural strength)
        """

        bala = {
            "sthana_bala": 0,
            "relationship_bala": 0,
            "naisargika_bala": 0,
            "total": 0,
            "status": "",
            "details": []
        }

        # 1. STHANA BALA (Positional Strength)

        # Exaltation check
        if planet in self.UCCHA:
            if sign == self.UCCHA[planet]["sign"]:
                bala["sthana_bala"] += 3
                bala["details"].append(planet + " is EXALTED (Uccha) in " + sign + " - Maximum strength")
            elif sign == self.NEECHA[planet]["sign"]:
                bala["sthana_bala"] -= 3
                bala["details"].append(planet + " is DEBILITATED (Neecha) in " + sign + " - Minimum strength")

        # Own sign check
        if planet in self.GRAHA_OWNERSHIP:
            if sign in self.GRAHA_OWNERSHIP[planet]:
                bala["sthana_bala"] += 2
                bala["details"].append(planet + " is in OWN sign (Swakshetra) " + sign + " - Strong")

        # Mool Trikona check
        if planet in self.MOOLTRIKONA:
            mt = self.MOOLTRIKONA[planet]
            if sign == mt["sign"] and mt["start"] <= degree <= mt["end"]:
                bala["sthana_bala"] += 2.5
                bala["details"].append(planet + " is in MOOLTRIKONA in " + sign + " - Very strong")

        # 2. RELATIONSHIP BALA (Friendship with sign lord)
        if planet in self.NAISARGIKA_MITRA:
            sign_lord = self._get_sign_lord(sign)
            if sign_lord and sign_lord != planet:
                if sign_lord in self.NAISARGIKA_MITRA[planet]["friends"]:
                    bala["relationship_bala"] += 1.5
                    bala["details"].append(planet + " is in FRIEND's sign (" + sign_lord + ") - Supportive")
                elif sign_lord in self.NAISARGIKA_MITRA[planet]["enemies"]:
                    bala["relationship_bala"] -= 1.5
                    bala["details"].append(planet + " is in ENEMY's sign (" + sign_lord + ") - Weakened")

        # 3. NAISARGIKA BALA (Natural Strength)
        natural_strength = {
            "Sun": 2.0, "Moon": 1.8, "Mars": 1.5,
            "Mercury": 1.7, "Jupiter": 2.2, "Venus": 1.9,
            "Saturn": 1.3, "Rahu": 1.0, "Ketu": 0.8
        }
        bala["naisargika_bala"] = natural_strength.get(planet, 1.0)

        # TOTAL
        bala["total"] = round(
            bala["sthana_bala"] +
            bala["relationship_bala"] +
            bala["naisargika_bala"],
            2
        )

        # Status classification
        if bala["total"] >= 5:
            bala["status"] = "VERY_STRONG"
        elif bala["total"] >= 3:
            bala["status"] = "STRONG"
        elif bala["total"] >= 1:
            bala["status"] = "MODERATE"
        elif bala["total"] >= -1:
            bala["status"] = "WEAK"
        else:
            bala["status"] = "VERY_WEAK"

        return bala

    def _get_sign_lord(self, sign):
        """Get lord of a sign"""
        for planet, signs in self.GRAHA_OWNERSHIP.items():
            if sign in signs:
                return planet
        return None

    def detect_dhana_yogas(self, positions):
        """
        Detect wealth yogas (BPHS Ch.41)
        Critical for market prediction
        """
        yogas = []

        # Get sign lords
        planet_signs = {}
        for planet, data in positions.items():
            planet_signs[planet] = data["sign"]

        # 1. Lakshmi Yoga: Venus + Lord of 9th strong
        venus_sign = planet_signs.get("Venus", "")
        if venus_sign in self.UCCHA.get("Venus", {}).get("sign", ""):
            yogas.append({
                "name": "Lakshmi Yoga",
                "type": "DHANA",
                "strength": "STRONG",
                "effect": "Wealth creation period. Markets favor luxury, auto, consumer sectors.",
                "planets": "Venus exalted"
            })

        # 2. Gajakesari Yoga: Jupiter-Moon in kendra
        jup_sign = planet_signs.get("Jupiter", "")
        moon_sign = planet_signs.get("Moon", "")
        if jup_sign == moon_sign:
            yogas.append({
                "name": "Gajakesari Yoga (Conjunction)",
                "type": "DHANA",
                "strength": "VERY_STRONG",
                "effect": "Bull market. Banking, finance sectors boom. Public sentiment very positive.",
                "planets": "Jupiter-Moon conjunct in " + jup_sign
            })

        # 3. Chandra-Mangal Yoga: Moon-Mars together
        mars_sign = planet_signs.get("Mars", "")
        if moon_sign == mars_sign:
            yogas.append({
                "name": "Chandra-Mangal Yoga",
                "type": "DHANA",
                "strength": "STRONG",
                "effect": "Real estate boom. Construction, metals, defense sectors strong. Emotional trading.",
                "planets": "Moon-Mars in " + moon_sign
            })

        # 4. Budh-Aditya Yoga: Sun-Mercury together
        sun_sign = planet_signs.get("Sun", "")
        merc_sign = planet_signs.get("Mercury", "")
        if sun_sign == merc_sign:
            yogas.append({
                "name": "Budh-Aditya Yoga",
                "type": "RAJA",
                "strength": "STRONG",
                "effect": "Government tech initiatives. IT, digital, PSU sectors benefit. Policy clarity.",
                "planets": "Sun-Mercury in " + sun_sign
            })

        # 5. Guru-Chandal Yoga: Jupiter-Rahu together (NEGATIVE)
        rahu_sign = planet_signs.get("Rahu", "")
        if jup_sign == rahu_sign:
            yogas.append({
                "name": "Guru-Chandal Yoga",
                "type": "DOSHA",
                "strength": "NEGATIVE",
                "effect": "Market manipulation risk. False rallies. Banking frauds possible. Be cautious.",
                "planets": "Jupiter-Rahu in " + jup_sign
            })

        # 6. Shani-Rahu Shrapit Yoga (NEGATIVE)
        sat_sign = planet_signs.get("Saturn", "")
        if sat_sign == rahu_sign:
            yogas.append({
                "name": "Shrapit Yoga",
                "type": "DOSHA",
                "strength": "VERY_NEGATIVE",
                "effect": "Major market disruption. Fear-driven selling. Infrastructure, oil sectors worst hit.",
                "planets": "Saturn-Rahu in " + sat_sign
            })

        # 7. Viparita Raja Yoga: Lords of 6,8,12 in each other's signs
        # Simplified check: debilitated planets can give unexpected gains
        for planet, data in positions.items():
            if planet in self.NEECHA:
                if data["sign"] == self.NEECHA[planet]["sign"]:
                    yogas.append({
                        "name": "Neechabhanga possibility for " + planet,
                        "type": "VIPARITA",
                        "strength": "MODERATE",
                        "effect": planet + " debilitated but may give unexpected turnaround in " + self.KARAKA.get(planet, "") + " related sectors.",
                        "planets": planet + " in " + data["sign"]
                    })

        # 8. Hamsa Yoga: Jupiter in kendra in own/exalted sign
        if jup_sign in ["Cancer", "Sagittarius", "Pisces"]:
            yogas.append({
                "name": "Hamsa Yoga",
                "type": "PANCHA_MAHAPURUSHA",
                "strength": "VERY_STRONG",
                "effect": "Wisdom prevails. Ethical investing rewarded. Finance, education, legal sectors boom.",
                "planets": "Jupiter in " + jup_sign
            })

        # 9. Malavya Yoga: Venus in kendra in own/exalted sign
        if venus_sign in ["Taurus", "Libra", "Pisces"]:
            yogas.append({
                "name": "Malavya Yoga",
                "type": "PANCHA_MAHAPURUSHA",
                "strength": "VERY_STRONG",
                "effect": "Luxury boom. Auto, entertainment, beauty, hospitality sectors thrive.",
                "planets": "Venus in " + venus_sign
            })

        # 10. Sasa Yoga: Saturn in kendra in own/exalted sign
        if sat_sign in ["Capricorn", "Aquarius", "Libra"]:
            yogas.append({
                "name": "Sasa Yoga",
                "type": "PANCHA_MAHAPURUSHA",
                "strength": "STRONG",
                "effect": "Discipline rewarded. Infrastructure, mining, oil sectors benefit. Value investing works.",
                "planets": "Saturn in " + sat_sign
            })

        # 11. Ruchaka Yoga: Mars in kendra in own/exalted sign
        if mars_sign in ["Aries", "Scorpio", "Capricorn"]:
            yogas.append({
                "name": "Ruchaka Yoga",
                "type": "PANCHA_MAHAPURUSHA",
                "strength": "STRONG",
                "effect": "Energy and aggression in markets. Defense, real estate, metals sectors strong.",
                "planets": "Mars in " + mars_sign
            })

        # 12. Bhadra Yoga: Mercury in kendra in own/exalted sign
        if merc_sign in ["Gemini", "Virgo"]:
            yogas.append({
                "name": "Bhadra Yoga",
                "type": "PANCHA_MAHAPURUSHA",
                "strength": "STRONG",
                "effect": "Intelligence wins. IT, communication, banking, media sectors excel.",
                "planets": "Mercury in " + merc_sign
            })

        return yogas

    def get_graha_avastha(self, planet, sign, degree):
        """
        Planetary state (BPHS Ch.45)
        Bala (Child), Kumara (Youth), Yuva (Adult), 
        Vruddha (Old), Mrita (Dead)
        """
        # Simplified: based on degree in sign
        if degree < 6:
            return {"state": "Bala (Child)", "strength_factor": 0.25, "market_effect": "New beginnings, weak but growing influence"}
        elif degree < 12:
            return {"state": "Kumara (Youth)", "strength_factor": 0.50, "market_effect": "Growing momentum, sector gaining strength"}
        elif degree < 18:
            return {"state": "Yuva (Adult)", "strength_factor": 1.00, "market_effect": "Peak influence, strongest market impact"}
        elif degree < 24:
            return {"state": "Vruddha (Old)", "strength_factor": 0.50, "market_effect": "Waning influence, sector losing steam"}
        else:
            return {"state": "Mrita (Dead)", "strength_factor": 0.125, "market_effect": "Minimal influence, sector bottoming out"}


class BNNSystem:
    """
    Brihat Nakshatra Nidhi calculations
    Detailed Nakshatra-based analysis for market prediction
    """

    # All 27 Nakshatras with financial attributes
    NAKSHATRAS = {
        "Ashwini": {
            "lord": "Ketu",
            "deity": "Ashwini Kumaras",
            "guna": "Rajas",
            "gana": "Deva",
            "tattva": "Earth",
            "financial_nature": "Quick gains, pharma, healing, speed",
            "market_effect": "Fast market moves, pharma rallies, quick trades favored",
            "sector_affinity": ["Pharma", "Healthcare", "Transport", "Racing"],
            "trading_style": "Aggressive short-term",
            "strength": 7
        },
        "Bharani": {
            "lord": "Venus",
            "deity": "Yama",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Earth",
            "financial_nature": "Transformation, death-rebirth of sectors",
            "market_effect": "Sector rotation, old stocks die, new ones born",
            "sector_affinity": ["Insurance", "Luxury", "Entertainment", "Fertility"],
            "trading_style": "Contrarian",
            "strength": 5
        },
        "Krittika": {
            "lord": "Sun",
            "deity": "Agni",
            "guna": "Rajas",
            "gana": "Rakshasa",
            "tattva": "Earth",
            "financial_nature": "Burning intensity, gold, authority",
            "market_effect": "Government actions impact market, gold moves, power sector",
            "sector_affinity": ["Gold", "Power", "Government", "Steel"],
            "trading_style": "Decisive, cut losses quickly",
            "strength": 6
        },
        "Rohini": {
            "lord": "Moon",
            "deity": "Brahma",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Earth",
            "financial_nature": "Growth, agriculture, beauty, creation",
            "market_effect": "Bull market energy, consumer stocks rise, agriculture boom",
            "sector_affinity": ["Agriculture", "FMCG", "Beauty", "Real Estate", "Luxury"],
            "trading_style": "Buy and hold",
            "strength": 9
        },
        "Mrigashira": {
            "lord": "Mars",
            "deity": "Soma",
            "guna": "Tamas",
            "gana": "Deva",
            "tattva": "Earth",
            "financial_nature": "Searching, research, exploration",
            "market_effect": "Market searching for direction, R&D stocks, exploration companies",
            "sector_affinity": ["Research", "Mining Exploration", "Textiles", "Perfume"],
            "trading_style": "Wait and watch",
            "strength": 5
        },
        "Ardra": {
            "lord": "Rahu",
            "deity": "Rudra",
            "guna": "Tamas",
            "gana": "Manushya",
            "tattva": "Water",
            "financial_nature": "Storms, destruction, technology disruption",
            "market_effect": "Market storms, tech disruption, sudden crashes possible",
            "sector_affinity": ["Technology", "Cyber", "Destruction/Construction", "Pharma"],
            "trading_style": "Hedge positions, expect volatility",
            "strength": 3
        },
        "Punarvasu": {
            "lord": "Jupiter",
            "deity": "Aditi",
            "guna": "Tamas",
            "gana": "Deva",
            "tattva": "Water",
            "financial_nature": "Return, renewal, restoration of wealth",
            "market_effect": "Market recovery, banking bounce, optimism returns",
            "sector_affinity": ["Banking", "Finance", "Education", "Hospitality"],
            "trading_style": "Buy the dip",
            "strength": 8
        },
        "Pushya": {
            "lord": "Saturn",
            "deity": "Brihaspati",
            "guna": "Tamas",
            "gana": "Deva",
            "tattva": "Water",
            "financial_nature": "MOST AUSPICIOUS for wealth. Nourishment.",
            "market_effect": "Best nakshatra for investments. Long-term buying opportunity.",
            "sector_affinity": ["All sectors", "Banking", "Dairy", "Education"],
            "trading_style": "Aggressive buying, SIP start",
            "strength": 10
        },
        "Ashlesha": {
            "lord": "Mercury",
            "deity": "Sarpa",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Water",
            "financial_nature": "Cunning, manipulation, hidden moves",
            "market_effect": "Insider trading risk, manipulation, IT sector volatile",
            "sector_affinity": ["Pharma", "Chemicals", "Poison/Pesticide", "IT"],
            "trading_style": "Be cautious, verify everything",
            "strength": 3
        },
        "Magha": {
            "lord": "Ketu",
            "deity": "Pitris",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Water",
            "financial_nature": "Authority, legacy, throne, power",
            "market_effect": "Blue-chip stocks favored, legacy companies strong",
            "sector_affinity": ["Government", "PSU", "Heritage", "Authority"],
            "trading_style": "Stick to large-caps",
            "strength": 7
        },
        "Purva Phalguni": {
            "lord": "Venus",
            "deity": "Bhaga",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Water",
            "financial_nature": "Enjoyment, luxury, partnerships",
            "market_effect": "Luxury stocks up, entertainment boom, partnership deals",
            "sector_affinity": ["Entertainment", "Luxury", "Hotels", "Weddings"],
            "trading_style": "Enjoy the ride, momentum trading",
            "strength": 7
        },
        "Uttara Phalguni": {
            "lord": "Sun",
            "deity": "Aryaman",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Fire",
            "financial_nature": "Contracts, agreements, patronage",
            "market_effect": "Corporate deals, M&A activity, government contracts",
            "sector_affinity": ["Government", "Corporate", "Contracts", "HR"],
            "trading_style": "Medium to long term",
            "strength": 7
        },
        "Hasta": {
            "lord": "Moon",
            "deity": "Savitar",
            "guna": "Rajas",
            "gana": "Deva",
            "tattva": "Fire",
            "financial_nature": "Skill, craftsmanship, trading skill",
            "market_effect": "Day trading favored, skilled traders profit, manufacturing",
            "sector_affinity": ["Manufacturing", "Crafts", "Trading", "Handicrafts"],
            "trading_style": "Active trading, use skills",
            "strength": 8
        },
        "Chitra": {
            "lord": "Mars",
            "deity": "Tvashtar",
            "guna": "Rajas",
            "gana": "Rakshasa",
            "tattva": "Fire",
            "financial_nature": "Design, architecture, brilliant creation",
            "market_effect": "Real estate design, tech innovation, creative destruction",
            "sector_affinity": ["Real Estate", "Architecture", "Design", "Fashion"],
            "trading_style": "Look for innovative companies",
            "strength": 6
        },
        "Swati": {
            "lord": "Rahu",
            "deity": "Vayu",
            "guna": "Rajas",
            "gana": "Deva",
            "tattva": "Fire",
            "financial_nature": "Trade, independence, movement, foreign",
            "market_effect": "International trade boost, forex moves, independent stocks",
            "sector_affinity": ["Trade", "Import/Export", "Aviation", "Forex"],
            "trading_style": "Go with the wind, trend following",
            "strength": 7
        },
        "Vishakha": {
            "lord": "Jupiter",
            "deity": "Indra-Agni",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Fire",
            "financial_nature": "Goal-oriented, determined, conquest",
            "market_effect": "Markets have clear direction, target-driven rallies",
            "sector_affinity": ["Banking", "Alcohol", "Agriculture", "Power"],
            "trading_style": "Set targets, be determined",
            "strength": 7
        },
        "Anuradha": {
            "lord": "Saturn",
            "deity": "Mitra",
            "guna": "Tamas",
            "gana": "Deva",
            "tattva": "Fire",
            "financial_nature": "Friendship, organization, devotion",
            "market_effect": "Institutional buying, organized sector movement",
            "sector_affinity": ["Institutions", "Organizations", "Mining", "Oil"],
            "trading_style": "Follow institutional money",
            "strength": 7
        },
        "Jyeshtha": {
            "lord": "Mercury",
            "deity": "Indra",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Air",
            "financial_nature": "Seniority, protection, chief",
            "market_effect": "Index leaders move, Nifty50 heavyweights lead",
            "sector_affinity": ["Large Cap", "Index", "Telecom", "IT"],
            "trading_style": "Trade the leaders",
            "strength": 6
        },
        "Mula": {
            "lord": "Ketu",
            "deity": "Nirriti",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Air",
            "financial_nature": "Root destruction, uprooting, pharma roots",
            "market_effect": "Market corrections, sector uprooting, pharma/chemicals",
            "sector_affinity": ["Pharma", "Chemicals", "Research", "Destruction"],
            "trading_style": "Avoid new positions, protect capital",
            "strength": 2
        },
        "Purva Ashadha": {
            "lord": "Venus",
            "deity": "Apas",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Air",
            "financial_nature": "Invincibility, water, early victory",
            "market_effect": "Initial rally phase, water/beverage sector, confidence building",
            "sector_affinity": ["Water", "Beverages", "Luxury", "Entertainment"],
            "trading_style": "Early entry, ride the wave",
            "strength": 7
        },
        "Uttara Ashadha": {
            "lord": "Sun",
            "deity": "Vishvadevas",
            "guna": "Rajas",
            "gana": "Manushya",
            "tattva": "Air",
            "financial_nature": "Final victory, universal, government",
            "market_effect": "Decisive market moves, government policy wins, blue-chips",
            "sector_affinity": ["Government", "PSU", "Defense", "Universal goods"],
            "trading_style": "Decisive action, commit fully",
            "strength": 8
        },
        "Shravana": {
            "lord": "Moon",
            "deity": "Vishnu",
            "guna": "Rajas",
            "gana": "Deva",
            "tattva": "Air",
            "financial_nature": "Listening, learning, media, knowledge",
            "market_effect": "News-driven market, media stocks, education sector",
            "sector_affinity": ["Media", "Education", "Knowledge", "Broadcasting"],
            "trading_style": "Listen to market signals",
            "strength": 8
        },
        "Dhanishta": {
            "lord": "Mars",
            "deity": "Vasus",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Ether",
            "financial_nature": "WEALTH nakshatra, abundance, music",
            "market_effect": "Wealth creation period, real estate, metals boom",
            "sector_affinity": ["Real Estate", "Metals", "Music", "Entertainment"],
            "trading_style": "Accumulate wealth-generating stocks",
            "strength": 9
        },
        "Shatabhisha": {
            "lord": "Rahu",
            "deity": "Varuna",
            "guna": "Tamas",
            "gana": "Rakshasa",
            "tattva": "Ether",
            "financial_nature": "Healing, hidden, 100 physicians",
            "market_effect": "Pharma/biotech rally, hidden value emerges, tech surprises",
            "sector_affinity": ["Pharma", "Biotech", "Technology", "Ocean/Water"],
            "trading_style": "Look for hidden gems",
            "strength": 5
        },
        "Purva Bhadrapada": {
            "lord": "Jupiter",
            "deity": "Ajaikapada",
            "guna": "Tamas",
            "gana": "Manushya",
            "tattva": "Ether",
            "financial_nature": "Burning platform, transformation, occult wealth",
            "market_effect": "Market transformation phase, banking reform, dramatic moves",
            "sector_affinity": ["Banking", "Finance", "Transformation", "Metals"],
            "trading_style": "Prepare for transformation",
            "strength": 5
        },
        "Uttara Bhadrapada": {
            "lord": "Saturn",
            "deity": "Ahirbudhnya",
            "guna": "Tamas",
            "gana": "Manushya",
            "tattva": "Ether",
            "financial_nature": "Deep ocean, kundalini wealth, hidden depths",
            "market_effect": "Deep value investing works, infrastructure, long-term gains",
            "sector_affinity": ["Infrastructure", "Oil", "Deep Mining", "Insurance"],
            "trading_style": "Deep value, long-term",
            "strength": 7
        },
        "Revati": {
            "lord": "Mercury",
            "deity": "Pushan",
            "guna": "Tamas",
            "gana": "Deva",
            "tattva": "Ether",
            "financial_nature": "Travel, completion, safe journey, prosperity",
            "market_effect": "Market completing a cycle, travel/tourism, safe investments",
            "sector_affinity": ["Travel", "Tourism", "Transport", "Fish/Ocean"],
            "trading_style": "Book profits, complete the cycle",
            "strength": 8
        }
    }

    # Vimshottari Dasha periods (years) - BNN
    VIMSHOTTARI_PERIODS = {
        "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
        "Mars": 7, "Rahu": 18, "Jupiter": 16,
        "Saturn": 19, "Mercury": 17
    }

    # Nakshatra sequence for Dasha
    NAKSHATRA_DASHA_LORD = {
        "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
        "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
        "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
        "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
        "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
        "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
        "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
        "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
        "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
    }

    # Tara Bala categories (BNN)
    TARA_CATEGORIES = {
        1: {"name": "Janma", "nature": "Mixed", "score": 5},
        2: {"name": "Sampat", "nature": "Wealth", "score": 9},
        3: {"name": "Vipat", "nature": "Danger", "score": 2},
        4: {"name": "Kshema", "nature": "Prosperity", "score": 8},
        5: {"name": "Pratyari", "nature": "Obstacle", "score": 3},
        6: {"name": "Sadhaka", "nature": "Achievement", "score": 8},
        7: {"name": "Vadha", "nature": "Death", "score": 1},
        8: {"name": "Mitra", "nature": "Friend", "score": 8},
        9: {"name": "Parama Mitra", "nature": "Best Friend", "score": 10}
    }

    def analyze_nakshatra(self, nakshatra_name):
        """Get complete BNN analysis for a nakshatra"""
        data = self.NAKSHATRAS.get(nakshatra_name, None)
        if not data:
            return {"error": "Nakshatra not found: " + nakshatra_name}
        return data

    def get_moon_nakshatra_analysis(self, positions):
        """
        Moon's nakshatra is crucial for market sentiment (BNN)
        """
        moon = positions.get("Moon", {})
        nakshatra = moon.get("nakshatra", "")
        data = self.analyze_nakshatra(nakshatra)

        if "error" in data:
            return data

        return {
            "moon_nakshatra": nakshatra,
            "lord": data["lord"],
            "market_effect": data["market_effect"],
            "sector_affinity": data["sector_affinity"],
            "trading_style": data["trading_style"],
            "strength": data["strength"],
            "guna": data["guna"],
            "financial_nature": data["financial_nature"]
        }

    def get_all_planet_nakshatras(self, positions):
        """Analyze all planets through their nakshatras"""
        results = {}
        for planet, data in positions.items():
            nak = data.get("nakshatra", "")
            nak_data = self.analyze_nakshatra(nak)
            if "error" not in nak_data:
                results[planet] = {
                    "nakshatra": nak,
                    "nak_lord": nak_data["lord"],
                    "financial_nature": nak_data["financial_nature"],
                    "market_effect": nak_data["market_effect"],
                    "strength": nak_data["strength"],
                    "sectors": nak_data["sector_affinity"]
                }
        return results

    def calculate_tara_bala(self, reference_nakshatra, transit_nakshatra):
        """
        Calculate Tara Bala (Star Strength) - BNN
        Used to judge if current transit is favorable
        """
        nak_list = list(self.NAKSHATRAS.keys())

        try:
            ref_idx = nak_list.index(reference_nakshatra)
            transit_idx = nak_list.index(transit_nakshatra)
        except ValueError:
            return {"error": "Invalid nakshatra"}

        diff = ((transit_idx - ref_idx) % 27) + 1
        tara_num = ((diff - 1) % 9) + 1

        tara = self.TARA_CATEGORIES[tara_num]

        return {
            "reference": reference_nakshatra,
            "transit": transit_nakshatra,
            "tara_number": tara_num,
            "tara_name": tara["name"],
            "nature": tara["nature"],
            "score": tara["score"],
            "favorable": tara["score"] >= 7
        }

    def get_market_nakshatra_score(self, positions):
        """
        Overall market score based on BNN analysis
        Considers Moon nakshatra + planet-nakshatra combinations
        """
        score = 5  # neutral
        details = []

        # Moon nakshatra is most important for market sentiment
        moon_analysis = self.get_moon_nakshatra_analysis(positions)
        if "error" not in moon_analysis:
            moon_strength = moon_analysis["strength"]
            score += (moon_strength - 5) * 0.5
            details.append(
                "Moon in " + moon_analysis["moon_nakshatra"] +
                " (Lord: " + moon_analysis["lord"] +
                ", Strength: " + str(moon_strength) + "/10): " +
                moon_analysis["market_effect"]
            )

        # Check all planets
        all_naks = self.get_all_planet_nakshatras(positions)
        for planet, data in all_naks.items():
            if planet == "Moon":
                continue
            nak_strength = data["strength"]
            weight = 0.15
            if planet in ["Jupiter", "Venus"]:
                weight = 0.25  # Benefics more important
            elif planet in ["Saturn", "Rahu"]:
                weight = 0.2  # Malefics significant

            score += (nak_strength - 5) * weight
            if nak_strength >= 8 or nak_strength <= 3:
                details.append(
                    planet + " in " + data["nakshatra"] +
                    " (" + str(nak_strength) + "/10): " +
                    data["market_effect"]
                )

        score = max(0, min(10, round(score, 1)))

        return {
            "bnn_score": score,
            "details": details,
            "moon_analysis": moon_analysis
        }


if __name__ == "__main__":
    print("=== BPHS System Test ===")
    bphs = BPHSSystem()

    # Test graha bala
    bala = bphs.calculate_graha_bala("Jupiter", "Cancer", 5, {})
    print("Jupiter in Cancer Bala:", bala["total"], bala["status"])
    for d in bala["details"]:
        print("  ", d)

    print("\n=== BNN System Test ===")
    bnn = BNNSystem()

    # Test nakshatra analysis
    pushya = bnn.analyze_nakshatra("Pushya")
    print("Pushya:", pushya["financial_nature"])
    print("Strength:", pushya["strength"])

    # Test tara bala
    tara = bnn.calculate_tara_bala("Rohini", "Pushya")
    print("\nTara Bala (Rohini->Pushya):", tara["tara_name"], "Score:", tara["score"])
