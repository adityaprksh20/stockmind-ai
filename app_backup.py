import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import json
from datetime import datetime

from engines.mamba_engine import get_balanced_llm, get_creative_llm
from engines.ephemeris_engine import EphemerisEngine
from agents.stock_data_agent import StockDataAgent
from agents.analysis_chain import StockAnalysisChain
from agents.sentiment_agent import SentimentAgent
from agents.jyotish_agent import JyotishAgent
from agents.unified_advisor import UnifiedAdvisor
from agents.prediction_engine import PredictionEngine, JyotishScorer
from config.settings import (
    FINANCIAL_DISCLAIMER,
    JYOTISH_DISCLAIMER,
    COMBINED_DISCLAIMER,
    NIFTY50_TICKERS,
    US_TICKERS,
    MUTUAL_FUNDS,
    "🧪 Backtest Jyotish",
)


# ============================================
# APP NAME & CONFIG
# ============================================
APP_NAME = "AstroInvest"
APP_TAGLINE = "AI + Vedic Astrology Powered Trading Intelligence"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CURRENCY HELPER
# ============================================
def get_currency(ticker):
    """Return currency symbol based on ticker"""
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "₹"
    elif ticker.endswith(".L"):
        return "£"
    elif ticker.endswith(".DE") or ticker.endswith(".PA"):
        return "€"
    elif ticker.endswith(".T"):
        return "¥"
    else:
        return "$"


def format_price(price, ticker):
    """Format price with correct currency"""
    c = get_currency(ticker)
    if price:
        return c + "{:,.2f}".format(float(price))
    return c + "N/A"


def format_market_cap(market_cap, ticker):
    """Format market cap with currency"""
    c = get_currency(ticker)
    if not market_cap:
        return "N/A"
    if market_cap >= 1e12:
        return c + "{:.2f}T".format(market_cap / 1e12)
    elif market_cap >= 1e9:
        return c + "{:.2f}B".format(market_cap / 1e9)
    elif market_cap >= 1e6:
        return c + "{:.2f}M".format(market_cap / 1e6)
    else:
        return c + str(market_cap)


# ============================================
# CUSTOM CSS
# ============================================
st.markdown(
    "<style>"
    ".main-header {"
    "  font-size: 2.5rem;"
    "  font-weight: bold;"
    "  background: linear-gradient("
    "    270deg,"
    "    #FF6B6B, #FF8E53, #FFE66D,"
    "    #4ECDC4, #45B7D1, #6C5CE7,"
    "    #A363D9, #FF6B6B"
    "  );"
    "  background-size: 200%;"
    "  -webkit-background-clip: text;"
    "  -webkit-text-fill-color: transparent;"
    "  background-clip: text;"
    "  text-align: center;"
    "  padding: 1rem 0;"
    "}"
    ".sub-header {"
    "  text-align: center;"
    "  color: #888;"
    "  font-size: 1.1rem;"
    "  margin-bottom: 2rem;"
    "}"
    ".disclaimer-box {"
    "  background: #fff3cd;"
    "  border: 1px solid #ffc107;"
    "  border-radius: 8px;"
    "  padding: 1rem;"
    "  font-size: 0.85rem;"
    "  color: #856404;"
    "}"
    "</style>",
    unsafe_allow_html=True
)
      

# ============================================
# CACHE AGENTS
# ============================================
@st.cache_resource
def load_stock_agent():
    return StockDataAgent()

@st.cache_resource
def load_analysis_chain():
    return StockAnalysisChain()

@st.cache_resource
def load_sentiment_agent():
    return SentimentAgent()

@st.cache_resource
def load_jyotish_agent():
    return JyotishAgent()

@st.cache_resource
def load_ephemeris():
    return EphemerisEngine()

@st.cache_resource
def load_unified_advisor():
    return UnifiedAdvisor()

@st.cache_resource
def load_prediction_engine():
    return PredictionEngine()

@st.cache_resource
def load_jyotish_scorer():
    return JyotishScorer()


# ============================================
# SIDEBAR - ALL MODES IN ONE LIST
# ============================================
ALL_MODES = [
    "🏠 Dashboard",
    "🎯 Stock Predictor",
    "📡 Market Scanner",
    "🏭 Sector Heatmap",
    "📊 Stock Analysis",
    "🔍 Stock Screener",
    "📰 Market Sentiment",
    "🪐 Jyotish Prediction",
    "🔮 World Events",
    "⭐ Stock Kundali",
    "🎯 Unified Advisor",
    "🔄 Sector Rotation",
    "💰 Mutual Funds",
]

with st.sidebar:
    st.markdown("## 🪐 " + APP_NAME)
    st.caption(APP_TAGLINE)
    st.markdown("---")

    mode = st.radio("Choose Mode", ALL_MODES, index=0)

    st.markdown("---")

    # LLM Status
    try:
        llm = get_balanced_llm()
        info = llm.get_info()
        st.success("🤖 " + info["label"])
    except Exception:
        st.error("LLM not configured")

    st.markdown("---")
    st.caption(
        "Not financial advice. Jyotish is speculative. "
        "Consult SEBI/SEC registered advisors."
    )


# ============================================
# DASHBOARD
# ============================================
if mode == "🏠 Dashboard":
    st.markdown(
        '<div class="main-header">🪐 ' + APP_NAME + '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">' + APP_TAGLINE + '</div>',
        unsafe_allow_html=True
    )

    try:
        ephemeris = load_ephemeris()
        report = ephemeris.get_market_report()

        col1, col2, col3 = st.columns(3)
        with col1:
            mood = report["market_mood"]
            if mood == "BULLISH":
                st.metric("🪐 Market Mood", "🟢 BULLISH")
            elif mood == "BEARISH":
                st.metric("🪐 Market Mood", "🔴 BEARISH")
            else:
                st.metric("🪐 Market Mood", "🟡 NEUTRAL")
        with col2:
            st.metric("⬆️ Positive Signals", report["positive_signals"])
        with col3:
            st.metric("⬇️ Negative Signals", report["negative_signals"])

        # Planetary Positions
        st.markdown("### 🪐 Current Planetary Positions (Vedic)")
        positions = report["planetary_positions"]
        planet_cols = st.columns(3)
        planet_emojis = {
            "Sun": "☀️", "Moon": "🌙", "Mars": "♂️",
            "Mercury": "☿️", "Jupiter": "♃", "Venus": "♀️",
            "Saturn": "♄", "Rahu": "🐉", "Ketu": "🔥"
        }
        for i, (planet, data) in enumerate(positions.items()):
            col = planet_cols[i % 3]
            emoji = planet_emojis.get(planet, "⭐")
            retro = " ℞" if data.get("retrograde") else ""
            with col:
                st.markdown(
                    "**" + emoji + " " + planet + retro + "**  \n" +
                    data["sign"] + " " + str(round(data["degree"], 1)) + "°  \n" +
                    "Nakshatra: " + data["nakshatra"]
                )

        # Yogas
        yogas = report["active_yogas"]
        if yogas:
            st.markdown("### ⭐ Active Market Yogas")
            for yoga in yogas[:8]:
                s = yoga["strength"]
                icon = "🟢" if s == "POSITIVE" else "🔵" if s == "STRONG" else "🔴" if s == "CAUTION" else "🟡"
                st.markdown(
                    icon + " **" + yoga["planets"] + "** (" +
                    yoga["type"] + "): " + yoga["significance"]
                )
    except Exception as e:
        st.error("Dashboard error: " + str(e))

    # Quick Stock Check
    st.markdown("---")
    st.markdown("### ⚡ Quick Stock Check")
    qcol1, qcol2 = st.columns([3, 1])
    with qcol1:
        quick_ticker = st.text_input("Ticker", "RELIANCE.NS", key="qt")
    with qcol2:
        st.markdown("<br>", unsafe_allow_html=True)
        quick_btn = st.button("Check", type="primary", key="qb")

    if quick_btn:
        try:
            agent = load_stock_agent()
            info = agent.get_stock_info(quick_ticker)
            if "error" not in info:
                c = get_currency(quick_ticker)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Price", format_price(info["current_price"], quick_ticker))
                c2.metric("📊 PE", str(info["pe_ratio"]))
                c3.metric("📈 52W High", format_price(info["52_week_high"], quick_ticker))
                c4.metric("📉 52W Low", format_price(info["52_week_low"], quick_ticker))
        except Exception as e:
            st.error(str(e))


# ============================================
# STOCK PREDICTOR
# ============================================
elif mode == "🎯 Stock Predictor":
    st.title("🎯 " + APP_NAME + " Stock Predictor")
    st.markdown("**Combined BUY/SELL signals** from Fundamentals + Technicals + Vedic Astrology")

    col1, col2 = st.columns([3, 1])
    with col1:
        pred_ticker = st.text_input("Stock Ticker", "RELIANCE.NS", key="pred_t")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("🎯 Predict", type="primary", key="pred_b")

    with st.expander("⚙️ Adjust Signal Weights"):
        w_fund = st.slider("Fundamental %", 0, 100, 40)
        w_tech = st.slider("Technical %", 0, 100, 30)
        w_jyot = st.slider("Jyotish %", 0, 100, 30)
        total = w_fund + w_tech + w_jyot
        if total > 0:
            weights = {
                "fundamental": w_fund / total,
                "technical": w_tech / total,
                "jyotish": w_jyot / total
            }
        else:
            weights = {"fundamental": 0.4, "technical": 0.3, "jyotish": 0.3}

    if predict_btn:
        with st.spinner("Analyzing " + pred_ticker + "..."):
            engine = load_prediction_engine()
            pred = engine.predict_stock(pred_ticker, weights)
            cur = get_currency(pred_ticker)

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Fundamental", str(pred["scores"]["fundamental"]) + "/10")
            c2.metric("📈 Technical", str(pred["scores"]["technical"]) + "/10")
            c3.metric("🪐 Jyotish", str(pred["scores"]["jyotish"]) + "/10")
            c4.metric("🎯 COMBINED", str(pred["scores"]["combined"]) + "/10")

            action = pred["action"]
            confidence = pred["confidence"]
            emoji = pred["emoji"]

            if "BUY" in action:
                st.success(emoji + " **" + action + "** | Confidence: " + str(confidence) + "%")
            elif "SELL" in action:
                st.error(emoji + " **" + action + "** | Confidence: " + str(confidence) + "%")
            else:
                st.warning(emoji + " **" + action + "** | Confidence: " + str(confidence) + "%")

            with st.expander("📊 Fundamental Details"):
                details = pred["fundamental_data"].get("details", {})
                finfo = pred["fundamental_data"].get("info", {})
                if finfo:
                    st.markdown("- **Price:** " + format_price(finfo.get("current_price", 0), pred_ticker))
                    st.markdown("- **Market Cap:** " + format_market_cap(finfo.get("market_cap", 0), pred_ticker))
                for key, val in details.items():
                    st.markdown("- **" + key + ":** " + str(val))

            with st.expander("📈 Technical Details"):
                tech = pred["technical_data"]
                if "error" not in tech:
                    st.markdown("- **Price:** " + format_price(tech.get("current_price", 0), pred_ticker))
                    st.markdown("- **RSI:** " + str(tech.get("rsi", "N/A")) + " (" + str(tech.get("rsi_signal", "")) + ")")
                    st.markdown("- **MACD Bullish:** " + str(tech.get("macd_bullish", "N/A")))
                    st.markdown("- **Above SMA 20:** " + str(tech.get("above_sma20", "N/A")))
                    st.markdown("- **Above SMA 50:** " + str(tech.get("above_sma50", "N/A")))
                    st.markdown("- **Volume Surge:** " + str(tech.get("volume_surge", "N/A")))

            with st.expander("🪐 Jyotish Details"):
                for r in pred["jyotish_data"].get("reasons", []):
                    st.markdown("- " + r)

            st.markdown("---")
            st.markdown("### 🤖 AI Report")
            with st.spinner("Generating report..."):
                report = engine.generate_ai_report(pred)
                st.markdown(report)

        st.warning(COMBINED_DISCLAIMER)


# ============================================
# MARKET SCANNER
# ============================================
elif mode == "📡 Market Scanner":
    st.title("📡 " + APP_NAME + " Market Scanner")
    st.markdown("Scan stocks for **best BUY/SELL** using combined analysis")

    market_choice = st.selectbox("Market", ["India - Nifty 50", "US - Top 20", "Both"])

    if market_choice == "India - Nifty 50":
        scan_tickers = NIFTY50_TICKERS[:15]
        cur = "₹"
    elif market_choice == "US - Top 20":
        scan_tickers = US_TICKERS[:15]
        cur = "$"
    else:
        scan_tickers = NIFTY50_TICKERS[:10] + US_TICKERS[:10]
        cur = "₹/$"

    st.info("Scanning " + str(len(scan_tickers)) + " stocks. Takes 1-2 minutes.")

    if st.button("📡 Scan Now", type="primary"):
        engine = load_prediction_engine()
        progress = st.progress(0)
        status = st.empty()
        results = []

        for i, ticker in enumerate(scan_tickers):
            status.text("Scanning " + ticker + "...")
            progress.progress((i + 1) / len(scan_tickers))
            try:
                pred = engine.predict_stock(ticker)
                results.append(pred)
            except Exception:
                continue

        progress.empty()
        status.empty()
        results.sort(key=lambda x: x["scores"]["combined"], reverse=True)

        st.markdown("### 🟢 TOP BUY SIGNALS")
        for r in results[:5]:
            c = get_currency(r["ticker"])
            price = r["fundamental_data"].get("info", {}).get("current_price", "N/A")
            st.markdown(
                r["emoji"] + " **" + r["ticker"] + "** " +
                c + str(price) + " | Score: **" +
                str(r["scores"]["combined"]) + "/10** | " +
                "F:" + str(r["scores"]["fundamental"]) + " " +
                "T:" + str(r["scores"]["technical"]) + " " +
                "J:" + str(r["scores"]["jyotish"]) + " | **" +
                r["action"] + "** (" + str(r["confidence"]) + "%)"
            )

        st.markdown("### 🔴 SELL/AVOID SIGNALS")
        for r in results[-3:]:
            c = get_currency(r["ticker"])
            st.markdown(
                r["emoji"] + " **" + r["ticker"] + "** | Score: **" +
                str(r["scores"]["combined"]) + "/10** | **" + r["action"] + "**"
            )

        with st.expander("📋 All Results"):
            for r in results:
                c = get_currency(r["ticker"])
                st.markdown(
                    r["emoji"] + " " + r["ticker"] + " | " +
                    str(r["scores"]["combined"]) + "/10 | " + r["action"]
                )

        st.markdown("---")
        st.markdown("### 🤖 AI Trading Plan")
        with st.spinner("Generating..."):
            scan_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_scanned": len(results),
                "top_buys": [r for r in results if r["scores"]["combined"] >= 6][:5],
                "top_sells": [r for r in results if r["scores"]["combined"] < 4][:3],
                "all_results": results
            }
            report = engine.generate_scan_report(scan_data)
            st.markdown(report)

        st.warning(COMBINED_DISCLAIMER)


# ============================================
# SECTOR HEATMAP
# ============================================
elif mode == "🏭 Sector Heatmap":
    st.title("🏭 Jyotish Sector Heatmap")
    st.markdown("Sector strength based on current planetary positions")

    if st.button("🪐 Generate Heatmap", type="primary"):
        with st.spinner("Calculating..."):
            scorer = load_jyotish_scorer()
            sectors = scorer.score_all_sectors()

            st.markdown("### Sector Rankings")
            for sector, data in sectors.items():
                score = data["score"]
                if score >= 7:
                    icon = "🟢"
                    label = "STRONG BUY"
                elif score >= 6:
                    icon = "🟢"
                    label = "BUY"
                elif score >= 4:
                    icon = "🟡"
                    label = "HOLD"
                else:
                    icon = "🔴"
                    label = "AVOID"

                support = ", ".join(data["supporting_planets"]) if data["supporting_planets"] else "None"
                oppose = ", ".join(data["opposing_planets"]) if data["opposing_planets"] else "None"

                st.markdown(icon + " **" + sector + "** — " + str(score) + "/10 — **" + label + "**")
                st.caption("Supporting: " + support + " | Opposing: " + oppose)

        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# STOCK ANALYSIS
# ============================================
elif mode == "📊 Stock Analysis":
    st.title("📊 AI Stock Analysis")

    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Market", ["India (NSE)", "US", "UK", "Europe", "Japan"])
    with col2:
        ticker_map = {
            "India (NSE)": (NIFTY50_TICKERS, "RELIANCE.NS"),
            "US": (US_TICKERS, "AAPL"),
            "UK": ([], "SHEL.L"),
            "Europe": ([], "SAP.DE"),
            "Japan": ([], "7203.T"),
        }
        tlist, default = ticker_map.get(market, ([], "AAPL"))
        if tlist:
            ticker = st.selectbox("Stock", ["Custom"] + tlist)
            if ticker == "Custom":
                ticker = st.text_input("Enter ticker", default)
        else:
            ticker = st.text_input("Enter ticker", default)

    if st.button("🔍 Analyze", type="primary"):
        with st.spinner("Analyzing " + ticker + "..."):
            agent = load_stock_agent()
            info = agent.get_stock_info(ticker)

            if "error" not in info:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Price", format_price(info["current_price"], ticker))
                c2.metric("📊 PE", str(info["pe_ratio"]))
                c3.metric("📈 ROE", str(round(info["roe"] * 100, 2)) + "%")
                c4.metric("🏦 Cap", format_market_cap(info["market_cap"], ticker))

            chain = load_analysis_chain()
            result = chain.analyze_stock(ticker)
            st.markdown("---")
            st.markdown(result)

        st.warning(FINANCIAL_DISCLAIMER)


# ============================================
# STOCK SCREENER
# ============================================
elif mode == "🔍 Stock Screener":
    st.title("🔍 Stock Screener")

    style = st.selectbox("Style", ["value", "growth", "dividend", "balanced"])
    descs = {
        "value": "Low PE, good ROE, undervalued",
        "growth": "High ROE, strong momentum",
        "dividend": "High yield, stable",
        "balanced": "Mix of value + growth"
    }
    st.info("📋 " + descs[style])

    if st.button("🎯 Screen", type="primary"):
        with st.spinner("Screening..."):
            chain = load_analysis_chain()
            result = chain.find_best_stocks(style)
            st.markdown(result)
        st.warning(FINANCIAL_DISCLAIMER)


# ============================================
# MARKET SENTIMENT
# ============================================
elif mode == "📰 Market Sentiment":
    st.title("📰 Market Sentiment")

    tab1, tab2 = st.tabs(["Stock Sentiment", "Market Overview"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            s_ticker = st.text_input("Ticker", "TCS.NS", key="st")
        with c2:
            s_company = st.text_input("Company", "TCS", key="sc")

        if st.button("📊 Analyze", key="sb"):
            with st.spinner("Analyzing..."):
                agent = load_sentiment_agent()
                result = agent.analyze_sentiment(s_ticker, s_company)
                st.markdown(result)
            st.warning(FINANCIAL_DISCLAIMER)

    with tab2:
        if st.button("🌍 Market Overview", key="mb"):
            with st.spinner("Analyzing..."):
                agent = load_sentiment_agent()
                result = agent.market_overview()
                st.markdown(result)
            st.warning(FINANCIAL_DISCLAIMER)


# ============================================
# JYOTISH PREDICTION
# ============================================
elif mode == "🪐 Jyotish Prediction":
    st.title("🪐 Jyotish Market Prediction")
    st.markdown(
        '<div class="disclaimer-box">'
        'Predictions based on Vedic Astrology. Speculative. Not financial advice.'
        '</div>', unsafe_allow_html=True
    )
    st.markdown("")

    if st.button("🔮 Get Prediction", type="primary"):
        with st.spinner("Consulting Navagrahas..."):
            agent = load_jyotish_agent()
            result = agent.predict_market_trend()
            st.markdown(result)
        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# WORLD EVENTS
# ============================================
elif mode == "🔮 World Events":
    st.title("🔮 World Events Prediction")
    st.markdown(
        '<div class="disclaimer-box">'
        'Mundane astrology predictions. Highly speculative.'
        '</div>', unsafe_allow_html=True
    )
    st.markdown("")

    if st.button("🌍 Predict", type="primary"):
        with st.spinner("Reading planetary alignments..."):
            agent = load_jyotish_agent()
            result = agent.world_events_prediction()
            st.markdown(result)
        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# STOCK KUNDALI
# ============================================
elif mode == "⭐ Stock Kundali":
    st.title("⭐ Stock Kundali")

    c1, c2 = st.columns(2)
    with c1:
        k_ticker = st.text_input("Ticker", "RELIANCE.NS", key="kt")
    with c2:
        k_date = st.date_input("Listing Date", datetime(1977, 5, 8))

    common = {
        "RELIANCE.NS": "1977-05-08",
        "TCS.NS": "2004-08-25",
        "INFY.NS": "1993-06-14",
        "HDFCBANK.NS": "1995-11-08",
        "AAPL": "1980-12-12",
        "MSFT": "1986-03-13",
        "GOOGL": "2004-08-19",
    }
    if k_ticker in common:
        st.info("Known listing: " + common[k_ticker])

    if st.button("⭐ Generate Kundali", type="primary"):
        with st.spinner("Creating horoscope..."):
            agent = load_jyotish_agent()
            result = agent.analyze_stock_astrology(k_ticker, k_date.strftime("%Y-%m-%d"))
            st.markdown(result)
        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# UNIFIED ADVISOR
# ============================================
elif mode == "🎯 Unified Advisor":
    st.title("🎯 Unified Advisor")
    st.markdown("Fundamental + Sentiment + Jyotish → ONE verdict")

    c1, c2, c3 = st.columns(3)
    with c1:
        u_ticker = st.text_input("Ticker", "RELIANCE.NS", key="ut")
    with c2:
        u_company = st.text_input("Company", "Reliance Industries", key="uc")
    with c3:
        u_listing = st.text_input("Listing Date", "1977-05-08", key="ul")

    if st.button("🎯 Analyze", type="primary", key="ub"):
        with st.spinner("Running 5 analyses... 1-2 minutes"):
            advisor = load_unified_advisor()
            result = advisor.complete_stock_analysis(
                u_ticker, u_company,
                u_listing if u_listing else None
            )

            with st.expander("📊 Fundamental"):
                st.markdown(str(result["analyses"].get("fundamental", "N/A")))
            with st.expander("📰 Sentiment"):
                st.markdown(str(result["analyses"].get("sentiment", "N/A")))

            planetary = result["analyses"].get("planetary", {})
            if isinstance(planetary, dict) and "market_mood" in planetary:
                with st.expander("🪐 Planetary"):
                    st.markdown("**Mood:** " + planetary.get("market_mood", "N/A"))
                    for y in planetary.get("active_yogas", [])[:5]:
                        st.markdown("- **" + y["planets"] + ":** " + y["significance"])

            with st.expander("🔮 Jyotish"):
                st.markdown(str(result["analyses"].get("jyotish", "N/A")))

            if "kundali" in result["analyses"]:
                with st.expander("⭐ Kundali"):
                    st.markdown(str(result["analyses"].get("kundali", "N/A")))

            st.markdown("---")
            st.markdown("## 🎯 COMBINED VERDICT")
            st.markdown(result.get("combined_verdict", "No verdict"))

        st.warning(COMBINED_DISCLAIMER)


# ============================================
# SECTOR ROTATION
# ============================================
elif mode == "🔄 Sector Rotation":
    st.title("🔄 Sector Rotation")
    st.markdown("Planet-based sector allocation")

    if st.button("🔄 Analyze", type="primary"):
        with st.spinner("Analyzing..."):
            advisor = load_unified_advisor()
            result = advisor.jyotish_sector_rotation()
            st.markdown(result)
        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# MUTUAL FUNDS
# ============================================
elif mode == "💰 Mutual Funds":
    st.title("💰 Mutual Fund Analysis")

    category = st.selectbox(
        "Category",
        list(MUTUAL_FUNDS.keys()) + ["Custom"]
    )

    if category == "Custom":
        fund_name = st.text_input("Fund Name", "SBI Bluechip Fund")
    else:
        fund_name = st.selectbox("Select Fund", MUTUAL_FUNDS[category])

    st.markdown("**Selected:** " + fund_name)

    if st.button("📊 Analyze Fund", type="primary", key="mf_btn"):
        with st.spinner("Analyzing " + fund_name + "..."):
            chain = load_analysis_chain()
            result = chain.analyze_mutual_fund(fund_name)

            if result and len(result) > 10:
                st.markdown(result)
            else:
                st.error("Could not generate analysis. Try again.")

        st.warning(FINANCIAL_DISCLAIMER)

# ============================================
# BACKTEST JYOTISH
# ============================================
elif mode == "🧪 Backtest Jyotish":
    st.title("🧪 Backtest: Does Jyotish Actually Work?")
    st.markdown(
        "**Honest validation** — tests if Jyotish signals "
        "correlate with actual market returns"
    )

    st.markdown(
        '<div class="disclaimer-box">'
        'This backtest compares Jyotish predictions against actual '
        'historical returns. Results may show Jyotish adds NO value. '
        'We believe in honest data over wishful thinking.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        bt_ticker = st.text_input("Stock to Backtest", "RELIANCE.NS", key="bt_t")
    with col2:
        bt_months = st.slider("Months of History", 3, 24, 12)

    if st.button("🧪 Run Backtest", type="primary"):
        from engines.backtester import MarketBacktester

        with st.spinner("Backtesting " + bt_ticker + " over " + str(bt_months) + " months... This takes 2-5 minutes."):
            bt = MarketBacktester()
            result = bt.backtest_stock(bt_ticker, bt_months)

            if "error" in result:
                st.error(result["error"])
            else:
                # Results
                st.markdown("---")
                st.markdown("### 📊 Backtest Results: " + bt_ticker)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("📈 Correlation", str(result["correlation"]))
                c2.metric("🟢 BUY Accuracy", str(result["buy_accuracy"]) + "%")
                c3.metric("🔴 SELL Accuracy", str(result["sell_accuracy"]) + "%")
                c4.metric("📊 Signals", str(result["total_signals"]))

                st.markdown("### 💰 Returns Comparison")
                c1, c2, c3 = st.columns(3)
                c1.metric("Buy & Hold", str(result["buy_hold_return"]) + "%")
                c2.metric("Jyotish Strategy", str(result["jyotish_strategy_return"]) + "%")
                outperf = result["jyotish_outperformance"]
                c3.metric(
                    "Outperformance",
                    str(outperf) + "%",
                    delta=str(outperf) + "%"
                )

                st.markdown("### 🔬 Component Analysis")
                st.markdown("Which Jyotish components correlate with actual returns:")
                for comp, corr in result["component_correlations"].items():
                    abs_corr = abs(corr)
                    if abs_corr > 0.15:
                        icon = "🟢 USEFUL"
                    elif abs_corr > 0.05:
                        icon = "🟡 WEAK"
                    else:
                        icon = "🔴 NO SIGNAL"
                    st.markdown(
                        icon + " **" + comp + "**: correlation = " + str(corr)
                    )

                # Verdict
                st.markdown("---")
                v = result["verdict"]
                st.markdown("### 🎯 HONEST VERDICT")

                if v["adds_value"]:
                    st.success(
                        "✅ **Jyotish adds value** for " + bt_ticker + "\n\n" +
                        v["honest_assessment"] + "\n\n" +
                        "Recommended weight in combined model: **" +
                        str(v["recommended_weight"]) + "%**"
                    )
                else:
                    st.error(
                        "❌ **Jyotish does NOT add value** for " + bt_ticker + "\n\n" +
                        v["honest_assessment"] + "\n\n" +
                        "Recommended weight: **0%** — rely on fundamentals + technicals"
                    )

                # Signal distribution
                with st.expander("📋 Detailed Signal Data"):
                    st.markdown("**Signal Distribution:**")
                    st.markdown("- BUY signals: " + str(result["buy_signals"]))
                    st.markdown("- SELL signals: " + str(result["sell_signals"]))
                    st.markdown("- NEUTRAL: " + str(result["neutral_signals"]))
                    st.markdown("")
                    st.markdown("**Average Returns by Signal:**")
                    st.markdown("- On BUY signal: " + str(result["avg_return_on_buy_signal"]) + "%")
                    st.markdown("- On SELL signal: " + str(result["avg_return_on_sell_signal"]) + "%")
                    st.markdown("- On NEUTRAL: " + str(result["avg_return_on_neutral"]) + "%")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; font-size: 0.8rem;">'
    '🪐 ' + APP_NAME + ' | ' + APP_TAGLINE + '<br>'
    'Supports: 🇮🇳 NSE/BSE (₹) | 🇺🇸 NYSE/NASDAQ ($) | '
    '🇬🇧 LSE (£) | 🇪🇺 EU (€) | 🇯🇵 TSE (¥)<br>'
    'Not financial advice. For educational purposes only.'
    '</div>',
    unsafe_allow_html=True
)
