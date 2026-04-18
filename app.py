from agents.prediction_engine import PredictionEngine, JyotishScorer
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import json
from datetime import datetime

# Import all agents
from engines.mamba_engine import get_balanced_llm, get_creative_llm
from engines.ephemeris_engine import EphemerisEngine
from agents.stock_data_agent import StockDataAgent
from agents.analysis_chain import StockAnalysisChain
from agents.sentiment_agent import SentimentAgent
from agents.jyotish_agent import JyotishAgent
from agents.unified_advisor import UnifiedAdvisor
from config.settings import (
    FINANCIAL_DISCLAIMER,
    JYOTISH_DISCLAIMER,
    COMBINED_DISCLAIMER,
    NIFTY50_TICKERS,
    US_TICKERS,
    MUTUAL_FUNDS
)


# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="StockMind + JyotishMarket AI",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B6B, #FFE66D, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .bullish { color: #00C851; font-weight: bold; }
    .bearish { color: #ff4444; font-weight: bold; }
    .neutral { color: #ffbb33; font-weight: bold; }
    .planet-card {
        background: #1a1a2e;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 3px solid #4ECDC4;
    }
    .disclaimer-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #856404;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# CACHE AGENTS (load once)
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


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🪐 StockMind + Jyotish AI")
    st.markdown("---")

    mode = st.radio(
        "Choose Mode",
        [
            "🏠 Dashboard",
            "📊 Stock Analysis",
            "🔍 Stock Screener",
            "📰 Market Sentiment",
            "🪐 Jyotish Prediction",
            "🔮 World Events",
            "⭐ Stock Kundali",
            "🎯 Unified Advisor",
            "🔄 Sector Rotation",
            "💰 Mutual Fund Analysis"
            "🎯 Stock Predictor",
            "📡 Market Scanner",
            "🏭 Sector Heatmap",
        ],
        index=0
    )

    st.markdown("---")

    # Show LLM info
    try:
        llm = get_balanced_llm()
        info = llm.get_info()
        st.success("🤖 " + info["label"])
    except Exception:
        st.error("❌ LLM not configured")

    st.markdown("---")
    st.markdown("### ⚠️ Disclaimers")
    st.caption(
        "Not financial advice. Jyotish predictions are speculative. "
        "Always consult SEBI-registered advisors."
    )

    st.markdown("---")
    st.markdown(
        "Built with Llama 4 + Vedic Astrology",
    )


# ============================================
# DASHBOARD
# ============================================
if mode == "🏠 Dashboard":
    st.markdown(
        '<div class="main-header">🪐 StockMind + JyotishMarket AI</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">'
        'AI-Powered Stock Analysis + Vedic Astrology Predictions'
        '</div>',
        unsafe_allow_html=True
    )

    # Planetary Dashboard
    try:
        ephemeris = load_ephemeris()
        report = ephemeris.get_market_report()

        col1, col2, col3 = st.columns(3)

        with col1:
            mood = report["market_mood"]
            if mood == "BULLISH":
                st.metric("🪐 Jyotish Market Mood", "🟢 BULLISH")
            elif mood == "BEARISH":
                st.metric("🪐 Jyotish Market Mood", "🔴 BEARISH")
            else:
                st.metric("🪐 Jyotish Market Mood", "🟡 NEUTRAL")

        with col2:
            st.metric(
                "⬆️ Positive Signals",
                report["positive_signals"]
            )

        with col3:
            st.metric(
                "⬇️ Negative Signals",
                report["negative_signals"]
            )

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
                    f"**{emoji} {planet}{retro}**  \n"
                    f"{data['sign']} {data['degree']:.1f}°  \n"
                    f"Nakshatra: {data['nakshatra']}"
                )

        # Active Yogas
        yogas = report["active_yogas"]
        if yogas:
            st.markdown("### ⭐ Active Market Yogas")
            for yoga in yogas[:8]:
                strength = yoga["strength"]
                if strength == "POSITIVE":
                    icon = "🟢"
                elif strength == "STRONG":
                    icon = "🔵"
                elif strength == "CAUTION":
                    icon = "🔴"
                else:
                    icon = "🟡"

                st.markdown(
                    f"{icon} **{yoga['planets']}** ({yoga['type']}): "
                    f"{yoga['significance']}"
                )

    except Exception as e:
        st.error("Dashboard error: " + str(e))

    # Quick Stock Check
    st.markdown("---")
    st.markdown("### ⚡ Quick Stock Check")

    qcol1, qcol2 = st.columns([3, 1])
    with qcol1:
        quick_ticker = st.text_input(
            "Enter ticker",
            "RELIANCE.NS",
            key="quick_ticker"
        )
    with qcol2:
        st.markdown("<br>", unsafe_allow_html=True)
        quick_check = st.button("Check", type="primary")

    if quick_check:
        try:
            agent = load_stock_agent()
            info = agent.get_stock_info(quick_ticker)

            if "error" not in info:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Price", str(info["current_price"]))
                c2.metric("📊 PE Ratio", str(info["pe_ratio"]))
                c3.metric(
                    "📈 52W High",
                    str(info["52_week_high"])
                )
                c4.metric(
                    "📉 52W Low",
                    str(info["52_week_low"])
                )
            else:
                st.error("Could not fetch data for " + quick_ticker)
        except Exception as e:
            st.error("Error: " + str(e))


# ============================================
# STOCK ANALYSIS
# ============================================
elif mode == "📊 Stock Analysis":
    st.title("📊 AI Stock Analysis")
    st.markdown("Comprehensive analysis powered by Llama 4 Maverick")

    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Market", ["India (NSE)", "US"])
    with col2:
        if market == "India (NSE)":
            ticker = st.selectbox(
                "Select Stock",
                ["Custom"] + NIFTY50_TICKERS
            )
            if ticker == "Custom":
                ticker = st.text_input(
                    "Enter NSE ticker",
                    "RELIANCE.NS"
                )
        else:
            ticker = st.selectbox(
                "Select Stock",
                ["Custom"] + US_TICKERS
            )
            if ticker == "Custom":
                ticker = st.text_input("Enter US ticker", "AAPL")

    if st.button("🔍 Analyze Stock", type="primary"):
        with st.spinner("Analyzing " + ticker + "..."):
            # Show basic data first
            agent = load_stock_agent()
            info = agent.get_stock_info(ticker)

            if "error" not in info:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Price", str(info["current_price"]))
                c2.metric("📊 PE", str(info["pe_ratio"]))
                c3.metric("📈 ROE", str(round(info["roe"] * 100, 2)) + "%")
                c4.metric("🏦 Market Cap", info["market_cap_formatted"])

            # AI Analysis
            chain = load_analysis_chain()
            result = chain.analyze_stock(ticker)
            st.markdown("---")
            st.markdown("### 🤖 AI Analysis")
            st.markdown(result)

        st.warning(FINANCIAL_DISCLAIMER)


# ============================================
# STOCK SCREENER
# ============================================
elif mode == "🔍 Stock Screener":
    st.title("🔍 AI Stock Screener")

    style = st.selectbox(
        "Investment Style",
        ["value", "growth", "dividend", "balanced"]
    )

    style_descriptions = {
        "value": "Low PE, good ROE, undervalued stocks",
        "growth": "High ROE, strong growth momentum",
        "dividend": "High dividend yield, stable companies",
        "balanced": "Mix of value and growth"
    }
    st.info("📋 " + style_descriptions[style])

    if st.button("🎯 Find Best Stocks", type="primary"):
        with st.spinner("Screening stocks... This may take a minute."):
            chain = load_analysis_chain()
            result = chain.find_best_stocks(style)
            st.markdown(result)

        st.warning(FINANCIAL_DISCLAIMER)


# ============================================
# MARKET SENTIMENT
# ============================================
elif mode == "📰 Market Sentiment":
    st.title("📰 Market Sentiment Analysis")

    tab1, tab2 = st.tabs(["Stock Sentiment", "Market Overview"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            sent_ticker = st.text_input("Stock Ticker", "TCS.NS")
        with col2:
            company_name = st.text_input("Company Name", "TCS")

        if st.button("📊 Analyze Sentiment", type="primary"):
            with st.spinner("Analyzing news sentiment..."):
                agent = load_sentiment_agent()
                result = agent.analyze_sentiment(
                    sent_ticker, company_name
                )
                st.markdown(result)
            st.warning(FINANCIAL_DISCLAIMER)

    with tab2:
        if st.button("🌍 Get Market Overview", type="primary"):
            with st.spinner("Analyzing market mood..."):
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
        '🪐 These predictions are based on Vedic Astrology (Jyotish) '
        'principles. They are speculative and should NOT be the sole '
        'basis for investment decisions.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    if st.button("🔮 Get Jyotish Market Prediction", type="primary"):
        with st.spinner("Consulting the Navagrahas... 🪐"):
            agent = load_jyotish_agent()
            result = agent.predict_market_trend()
            st.markdown(result)

        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# WORLD EVENTS
# ============================================
elif mode == "🔮 World Events":
    st.title("🔮 Medini Jyotish - World Events Prediction")

    st.markdown(
        '<div class="disclaimer-box">'
        '🔮 Mundane astrology (Medini Jyotish) predictions are highly '
        'speculative. For educational and entertainment purposes only.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    if st.button("🌍 Predict World Events & Market Impact", type="primary"):
        with st.spinner("Reading planetary alignments... 🪐"):
            agent = load_jyotish_agent()
            result = agent.world_events_prediction()
            st.markdown(result)

        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# STOCK KUNDALI
# ============================================
elif mode == "⭐ Stock Kundali":
    st.title("⭐ Stock Kundali (Horoscope)")

    col1, col2 = st.columns(2)
    with col1:
        kundali_ticker = st.text_input(
            "Stock Ticker",
            "RELIANCE.NS",
            key="kundali_ticker"
        )
    with col2:
        listing_date = st.date_input(
            "Listing Date (approx)",
            datetime(1977, 5, 8)
        )

    common_dates = {
        "RELIANCE.NS": "1977-05-08",
        "TCS.NS": "2004-08-25",
        "INFY.NS": "1993-06-14",
        "HDFCBANK.NS": "1995-11-08",
        "ITC.NS": "1970-08-24",
    }

    if kundali_ticker in common_dates:
        st.info(
            "Known listing date for " + kundali_ticker +
            ": " + common_dates[kundali_ticker]
        )

    if st.button("⭐ Generate Stock Kundali", type="primary"):
        with st.spinner("Creating stock horoscope... ⭐"):
            agent = load_jyotish_agent()
            result = agent.analyze_stock_astrology(
                kundali_ticker,
                listing_date.strftime("%Y-%m-%d")
            )
            st.markdown(result)

        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# UNIFIED ADVISOR (Stock + Jyotish Combined)
# ============================================
elif mode == "🎯 Unified Advisor":
    st.title("🎯 Unified Advisor")
    st.markdown(
        "**The Ultimate Analysis:** Combines Fundamental Analysis + "
        "Market Sentiment + Vedic Astrology into ONE recommendation"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        unified_ticker = st.text_input(
            "Stock Ticker",
            "RELIANCE.NS",
            key="unified_ticker"
        )
    with col2:
        unified_company = st.text_input(
            "Company Name",
            "Reliance Industries",
            key="unified_company"
        )
    with col3:
        unified_listing = st.text_input(
            "Listing Date (optional)",
            "1977-05-08",
            key="unified_listing"
        )

    if st.button("🎯 Get Unified Analysis", type="primary"):
        with st.spinner(
            "Running 5 analyses in parallel... This takes 1-2 minutes"
        ):
            advisor = load_unified_advisor()
            result = advisor.complete_stock_analysis(
                unified_ticker,
                unified_company,
                unified_listing if unified_listing else None
            )

            # Show individual analyses
            st.markdown("---")

            with st.expander("📊 Fundamental Analysis", expanded=False):
                st.markdown(
                    str(result["analyses"].get("fundamental", "N/A"))
                )

            with st.expander("📰 Sentiment Analysis", expanded=False):
                st.markdown(
                    str(result["analyses"].get("sentiment", "N/A"))
                )

            planetary = result["analyses"].get("planetary", {})
            if isinstance(planetary, dict) and "market_mood" in planetary:
                with st.expander("🪐 Planetary State", expanded=False):
                    st.markdown(
                        "**Market Mood:** " +
                        planetary.get("market_mood", "N/A")
                    )
                    yogas = planetary.get("active_yogas", [])
                    for y in yogas[:5]:
                        st.markdown(
                            "- **" + y["planets"] + "**: " +
                            y["significance"]
                        )

            with st.expander("🔮 Jyotish Prediction", expanded=False):
                st.markdown(
                    str(result["analyses"].get("jyotish", "N/A"))
                )

            if "kundali" in result["analyses"]:
                with st.expander("⭐ Stock Kundali", expanded=False):
                    st.markdown(
                        str(result["analyses"].get("kundali", "N/A"))
                    )

            # Combined Verdict (Main Output)
            st.markdown("---")
            st.markdown("## 🎯 COMBINED VERDICT")
            st.markdown(result.get("combined_verdict", "No verdict generated"))

        st.warning(COMBINED_DISCLAIMER)


# ============================================
# SECTOR ROTATION
# ============================================
elif mode == "🔄 Sector Rotation":
    st.title("🔄 Jyotish Sector Rotation")
    st.markdown(
        "Which sectors to overweight/underweight based on "
        "current planetary positions"
    )

    if st.button("🔄 Get Sector Rotation Advice", type="primary"):
        with st.spinner("Analyzing planetary sector influence..."):
            advisor = load_unified_advisor()
            result = advisor.jyotish_sector_rotation()
            st.markdown(result)

        st.warning(JYOTISH_DISCLAIMER)


# ============================================
# MUTUAL FUND ANALYSIS
# ============================================
elif mode == "💰 Mutual Fund Analysis":
    st.title("💰 Mutual Fund Analysis")

    # Category selection
    category = st.selectbox(
        "Fund Category",
        list(MUTUAL_FUNDS.keys()) + ["Custom"]
    )

    if category == "Custom":
        fund_name = st.text_input(
            "Enter Fund Name",
            "SBI Bluechip Fund"
        )
    else:
        fund_name = st.selectbox(
            "Select Fund",
            MUTUAL_FUNDS[category]
        )

    if st.button("📊 Analyze Fund", type="primary"):
        with st.spinner("Analyzing " + fund_name + "..."):
            chain = load_analysis_chain()
            result = chain.analyze_mutual_fund(fund_name)
            st.markdown(result)

        st.warning(FINANCIAL_DISCLAIMER)

# ============================================
# STOCK PREDICTOR
# ============================================
elif mode == "🎯 Stock Predictor":
    st.title("🎯 AI + Jyotish Stock Predictor")
    st.markdown(
        "**Combined BUY/SELL signals** from Fundamentals + "
        "Technicals + Vedic Astrology"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        pred_ticker = st.text_input(
            "Enter Stock Ticker",
            "RELIANCE.NS",
            key="pred_ticker"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("🎯 Predict", type="primary")

    # Weight adjustment
    with st.expander("⚙️ Adjust Signal Weights"):
        st.markdown("How much to trust each signal source:")
        w_fund = st.slider("Fundamental Weight", 0, 100, 40, key="w_fund")
        w_tech = st.slider("Technical Weight", 0, 100, 30, key="w_tech")
        w_jyot = st.slider("Jyotish Weight", 0, 100, 30, key="w_jyot")

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
        with st.spinner("Analyzing " + pred_ticker + " across 3 dimensions..."):
            engine = PredictionEngine()
            pred = engine.predict_stock(pred_ticker, weights)

            # Score Cards
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "📊 Fundamental",
                    str(pred["scores"]["fundamental"]) + "/10"
                )
            with c2:
                st.metric(
                    "📈 Technical",
                    str(pred["scores"]["technical"]) + "/10"
                )
            with c3:
                st.metric(
                    "🪐 Jyotish",
                    str(pred["scores"]["jyotish"]) + "/10"
                )
            with c4:
                st.metric(
                    "🎯 COMBINED",
                    str(pred["scores"]["combined"]) + "/10"
                )

            # Action Banner
            action = pred["action"]
            confidence = pred["confidence"]
            emoji = pred["emoji"]

            if "BUY" in action:
                st.success(
                    emoji + " **" + action + "** | "
                    "Confidence: " + str(confidence) + "%"
                )
            elif "SELL" in action:
                st.error(
                    emoji + " **" + action + "** | "
                    "Confidence: " + str(confidence) + "%"
                )
            else:
                st.warning(
                    emoji + " **" + action + "** | "
                    "Confidence: " + str(confidence) + "%"
                )

            # Detailed Breakdown
            with st.expander("📊 Fundamental Details"):
                details = pred["fundamental_data"].get("details", {})
                if details:
                    for key, val in details.items():
                        st.markdown("- **" + key + ":** " + str(val))

            with st.expander("📈 Technical Details"):
                tech = pred["technical_data"]
                if "error" not in tech:
                    st.markdown("- **RSI:** " + str(tech.get("rsi", "N/A")) + " (" + str(tech.get("rsi_signal", "")) + ")")
                    st.markdown("- **MACD Bullish:** " + str(tech.get("macd_bullish", "N/A")))
                    st.markdown("- **Above SMA 20:** " + str(tech.get("above_sma20", "N/A")))
                    st.markdown("- **Above SMA 50:** " + str(tech.get("above_sma50", "N/A")))
                    st.markdown("- **Volume Surge:** " + str(tech.get("volume_surge", "N/A")))

            with st.expander("🪐 Jyotish Details"):
                reasons = pred["jyotish_data"].get("reasons", [])
                for r in reasons:
                    st.markdown("- " + r)

            # AI Report
            st.markdown("---")
            st.markdown("### 🤖 AI Analysis Report")
            with st.spinner("Generating detailed report..."):
                report = engine.generate_ai_report(pred)
                st.markdown(report)

        st.warning(COMBINED_DISCLAIMER)


# ============================================
# MARKET SCANNER
# ============================================
elif mode == "📡 Market Scanner":
    st.title("📡 AI Market Scanner")
    st.markdown(
        "Scans stocks and finds the **best BUY and SELL** "
        "opportunities using combined analysis"
    )

    market_choice = st.selectbox(
        "Market",
        ["India - Nifty 50", "US - Top 20", "Both"]
    )

    if market_choice == "India - Nifty 50":
        scan_tickers = NIFTY50_TICKERS[:15]
    elif market_choice == "US - Top 20":
        scan_tickers = US_TICKERS[:15]
    else:
        scan_tickers = NIFTY50_TICKERS[:10] + US_TICKERS[:10]

    st.info("Will scan " + str(len(scan_tickers)) + " stocks. Takes 1-2 minutes.")

    if st.button("📡 Scan Market Now", type="primary"):
        engine = PredictionEngine()

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

        results.sort(
            key=lambda x: x["scores"]["combined"],
            reverse=True
        )

        # Top Buys
        st.markdown("### 🟢 TOP BUY SIGNALS")
        for r in results[:5]:
            score = r["scores"]["combined"]
            st.markdown(
                r["emoji"] + " **" + r["ticker"] + "** | "
                "Combined: **" + str(score) + "/10** | "
                "F:" + str(r["scores"]["fundamental"]) + " "
                "T:" + str(r["scores"]["technical"]) + " "
                "J:" + str(r["scores"]["jyotish"]) + " | "
                "**" + r["action"] + "** (" +
                str(r["confidence"]) + "% confidence)"
            )

        # Top Sells
        st.markdown("### 🔴 TOP SELL/AVOID SIGNALS")
        for r in results[-3:]:
            score = r["scores"]["combined"]
            st.markdown(
                r["emoji"] + " **" + r["ticker"] + "** | "
                "Combined: **" + str(score) + "/10** | "
                "**" + r["action"] + "**"
            )

        # Full Table
        with st.expander("📋 Full Scan Results"):
            for r in results:
                st.markdown(
                    r["emoji"] + " " + r["ticker"] + " | " +
                    str(r["scores"]["combined"]) + "/10 | " +
                    r["action"]
                )

        # AI Report
        st.markdown("---")
        st.markdown("### 🤖 AI Market Report")
        with st.spinner("Generating trading plan..."):
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

    if st.button("🪐 Generate Sector Heatmap", type="primary"):
        with st.spinner("Calculating planetary sector influence..."):
            scorer = JyotishScorer()
            sectors = scorer.score_all_sectors()

            st.markdown("### Sector Rankings (Jyotish-Based)")

            for sector, data in sectors.items():
                score = data["score"]

                if score >= 7:
                    bar_color = "🟢"
                    label = "STRONG BUY"
                elif score >= 6:
                    bar_color = "🟢"
                    label = "BUY"
                elif score >= 4:
                    bar_color = "🟡"
                    label = "HOLD"
                else:
                    bar_color = "🔴"
                    label = "AVOID"

                support = ", ".join(data["supporting_planets"]) if data["supporting_planets"] else "None"
                oppose = ", ".join(data["opposing_planets"]) if data["opposing_planets"] else "None"

                st.markdown(
                    bar_color + " **" + sector + "** — " +
                    str(score) + "/10 — **" + label + "**"
                )
                st.caption(
                    "   Supporting: " + support +
                    " | Opposing: " + oppose
                )

        st.warning(JYOTISH_DISCLAIMER)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; font-size: 0.8rem;">'
    '🪐 StockMind + JyotishMarket AI | '
    'Powered by Llama 4 Maverick + Vedic Astrology<br>'
    'Not financial advice. For educational purposes only.'
    '</div>',
    unsafe_allow_html=True
)
