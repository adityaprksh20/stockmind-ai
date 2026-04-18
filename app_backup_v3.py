import streamlit as st
import os

st.set_page_config(
    page_title="StockMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)

from datetime import datetime
from engines.market_engine import (
    fetch_market_data, fmt, fmt_large, chg_arrow,
    ASSET_EXAMPLES, DEFAULT_WATCHLIST,
)


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## StockMind AI")
    st.caption("Market Intelligence for Global Assets")
    st.markdown("---")

    use_jyotish = st.toggle("Vedic Jyotish Layer", value=False)
    if use_jyotish:
        st.caption("Planetary signals added to verdict")
    else:
        st.caption("Pure market analysis only")

    st.markdown("---")

    modes = ["Analyze", "Watchlist"]
    if use_jyotish:
        modes.append("Validate Jyotish")
    mode = st.radio("Mode", modes, label_visibility="collapsed")

    st.markdown("---")

    with st.expander("Supported Assets"):
        for category, tickers in ASSET_EXAMPLES.items():
            st.markdown("**" + category + "**")
            st.caption(", ".join(tickers))

    st.markdown(
        '<div class="disclaimer-box">'
        "Not financial advice. Jyotish signals are experimental."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════
# HELPER: JYOTISH
# ═══════════════════════════════════════════════════════
def calculate_jyotish():
    from engines.ephemeris_engine import EphemerisEngine
    from engines.vedic_core import BPHSSystem, BNNSystem

    eph = EphemerisEngine()
    bphs = BPHSSystem()
    bnn = BNNSystem()
    now = datetime.now()
    positions = eph.get_planetary_positions(now)

    j_score = 50
    planet_details = []

    for planet, data in positions.items():
        bala = bphs.calculate_graha_bala(
            planet, data["sign"], data["degree"], positions
        )
        adj = 0
        if planet in ["Jupiter", "Venus", "Mercury"]:
            if bala["status"] in ["VERY_STRONG", "STRONG"]:
                adj = 2
            elif bala["status"] == "VERY_WEAK":
                adj = -2
        if planet == "Moon":
            if bala["status"] in ["VERY_STRONG", "STRONG"]:
                adj = 3
            elif bala["status"] == "VERY_WEAK":
                adj = -3
        if planet in ["Saturn", "Mars"] and bala["status"] == "VERY_WEAK":
            adj = -2

        j_score += adj
        planet_details.append({
            "planet": planet,
            "sign": data["sign"],
            "degree": round(data["degree"], 1),
            "retro": data.get("retrograde", False),
            "status": bala["status"],
            "adj": adj,
        })

    dhana_yogas = bphs.detect_dhana_yogas(positions)
    for y in dhana_yogas:
        if y["strength"] in ["VERY_STRONG", "STRONG"]:
            j_score += 3
        elif y["strength"] in ["NEGATIVE", "VERY_NEGATIVE"]:
            j_score -= 4

    bnn_result = bnn.get_market_nakshatra_score(positions)
    bnn_val = bnn_result.get("bnn_score", 5)
    j_score += (bnn_val - 5) * 1.5

    moon_analysis = bnn.get_moon_nakshatra_analysis(positions)
    retro_count = sum(
        1 for p, d in positions.items()
        if d.get("retrograde") and p not in ["Rahu", "Ketu"]
    )
    j_score -= retro_count * 1.5
    j_score = max(0, min(100, round(j_score, 1)))

    j_signal = (
        "STRONG_BUY" if j_score >= 70 else
        "BUY" if j_score >= 60 else
        "NEUTRAL" if j_score >= 40 else
        "SELL" if j_score >= 30 else
        "STRONG_SELL"
    )

    moon_nak = "-"
    if "error" not in moon_analysis:
        moon_nak = moon_analysis.get("nakshatra", "-")

    return {
        "score": j_score,
        "signal": j_signal,
        "bnn_score": bnn_val,
        "retro_count": retro_count,
        "dhana_yogas": dhana_yogas,
        "moon_nakshatra": moon_nak,
        "planets": planet_details,
    }


def signal_pill(signal):
    colors = {
        "BULLISH": "pill-green", "STRONG_BUY": "pill-green", "BUY": "pill-green",
        "BEARISH": "pill-red", "STRONG_SELL": "pill-red", "SELL": "pill-red",
        "NEUTRAL": "pill-yellow", "HOLD": "pill-yellow",
    }
    css = colors.get(signal, "pill-blue")
    return '<span class="pill ' + css + '">' + signal + "</span>"


def combined_verdict(tech_score, fund_score, j_score=None, use_j=False):
    if use_j and j_score is not None:
        w_t, w_f, w_j = 0.30, 0.45, 0.25
        score = round(tech_score * w_t + fund_score * w_f + j_score * w_j, 1)
        weights = "Tech " + str(int(w_t * 100)) + "% | Fund " + str(int(w_f * 100)) + "% | Jyotish " + str(int(w_j * 100)) + "%"
    else:
        w_t, w_f = 0.40, 0.60
        score = round(tech_score * w_t + fund_score * w_f, 1)
        weights = "Tech " + str(int(w_t * 100)) + "% | Fund " + str(int(w_f * 100)) + "%"

    signal = (
        "STRONG BUY" if score >= 72 else
        "BUY" if score >= 58 else
        "HOLD" if score >= 42 else
        "SELL" if score >= 28 else
        "STRONG SELL"
    )
    return score, signal, weights


# ═══════════════════════════════════════════════════════
# MODE 1: ANALYZE
# ═══════════════════════════════════════════════════════
if mode == "Analyze":
    st.markdown("# Analyze")

    col_t, col_h, col_go = st.columns([3, 2, 1])
    with col_t:
        ticker = st.text_input(
            "Ticker / Symbol",
            "RELIANCE.NS",
            placeholder="AAPL, TCS.NS, SPY, BTC-USD...",
        )
    with col_h:
        horizon = st.selectbox("Horizon", ["1 Week", "1 Month", "3 Months", "1 Year"])
    with col_go:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Analyze", type="primary", use_container_width=True)

    if run and ticker.strip():
        ticker = ticker.strip().upper()

        with st.spinner("Fetching " + ticker + "..."):
            d = fetch_market_data(ticker)

        if "error" in d:
            st.error(d["error"])
            st.stop()

        j = None
        if use_jyotish:
            with st.spinner("Calculating Jyotish..."):
                j = calculate_jyotish()

        # HEADER
        st.markdown("---")
        st.markdown(
            "### " + d["name"] + " &nbsp;&nbsp;" + signal_pill(d["asset_type"]),
            unsafe_allow_html=True,
        )

        h1, h2, h3, h4, h5 = st.columns(5)
        h1.metric("Price", d["currency"] + str(d["price"]), str(d["chg_1d"]) + "% today")
        h2.metric("1 Week", chg_arrow(d["chg_1w"]))
        h3.metric("1 Month", chg_arrow(d["chg_1m"]))
        h4.metric("1 Year", chg_arrow(d["chg_1y"]))
        h5.metric("From 52W High", str(d["from_high"]) + "%")

        # THREE PILLARS
        st.markdown('<div class="section-label">Signal Breakdown</div>', unsafe_allow_html=True)

        if use_jyotish and j:
            col_tech, col_fund, col_jyo = st.columns(3)
        else:
            col_tech, col_fund = st.columns(2)
            col_jyo = None

        with col_tech:
            st.markdown(
                '<div class="signal-card"><h4>Technical</h4>'
                '<div class="value">' + signal_pill(d["tech_signal"]) +
                " &nbsp; " + str(d["tech_score"]) + "/100</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown("**Trend**")
            st.markdown("SMA 20: " + d["currency"] + str(d["sma_20"]) + ("  ✅" if d["price"] > d["sma_20"] else "  ⚠️"))
            st.markdown("SMA 50: " + d["currency"] + str(d["sma_50"]) + ("  ✅" if d["price"] > d["sma_50"] else "  ⚠️"))
            if d["sma_200"]:
                st.markdown("SMA 200: " + d["currency"] + str(d["sma_200"]) + ("  ✅" if d["price"] > d["sma_200"] else "  ⚠️"))
            st.markdown("**Momentum**")
            rsi_tag = " Overbought" if d["rsi"] > 70 else " Oversold" if d["rsi"] < 30 else " Normal"
            st.markdown("RSI (14): " + str(d["rsi"]) + rsi_tag)
            st.markdown("MACD: " + str(d["macd"]) + ("  ✅ Bullish" if d["macd"] > 0 else "  ⚠️ Bearish"))
            st.markdown("**Volatility**")
            st.markdown("Bollinger: " + d["currency"] + str(d["bb_lower"]) + " - " + d["currency"] + str(d["bb_upper"]))
            vol_ratio = round(d["vol_today"] / d["vol_avg"], 1) if d["vol_avg"] > 0 else 0
            st.markdown("Volume: " + str(vol_ratio) + "x avg")

        with col_fund:
            st.markdown(
                '<div class="signal-card"><h4>Fundamental</h4>'
                '<div class="value">' + signal_pill(d["fund_signal"]) +
                " &nbsp; " + str(d["fund_score"]) + "/100</div></div>",
                unsafe_allow_html=True,
            )

            if d["asset_type"] in ["ETF", "Mutual Fund"]:
                st.markdown("**Fund Metrics**")
                st.markdown("NAV: " + fmt(d["nav"], prefix=d["currency"]))
                st.markdown("Expense Ratio: " + fmt(d["expense_ratio"], suffix="%", mult=100))
                st.markdown("Total Assets: " + fmt_large(d["total_assets"]))
                st.markdown("YTD Return: " + fmt(d["ytd_return"], suffix="%", mult=100))
                st.markdown("3Y Return: " + fmt(d["three_yr_return"], suffix="%", mult=100))
                st.markdown("5Y Return: " + fmt(d["five_yr_return"], suffix="%", mult=100))
            else:
                st.markdown("**Valuation**")
                pe_display = fmt(d["pe"])
                if d["pe"]:
                    pe_display += "  ✅" if d["pe"] < 25 else ("  ⚠️" if d["pe"] > 40 else "")
                st.markdown("P/E: " + pe_display)
                st.markdown("Fwd P/E: " + fmt(d["fwd_pe"]))
                st.markdown("P/B: " + fmt(d["pb"]))
                st.markdown("P/S: " + fmt(d["ps"]))
                st.markdown("**Quality**")
                roe_display = fmt(d["roe"], suffix="%", mult=100)
                if d["roe"] and d["roe"] > 0.15:
                    roe_display += "  ✅"
                st.markdown("ROE: " + roe_display)
                st.markdown("Profit Margin: " + fmt(d["profit_margin"], suffix="%", mult=100))
                de_display = fmt(d["debt_eq"])
                if d["debt_eq"] is not None:
                    de_display += "  ✅" if d["debt_eq"] < 100 else ("  ⚠️" if d["debt_eq"] > 200 else "")
                st.markdown("Debt/Equity: " + de_display)
                st.markdown("**Growth**")
                st.markdown("Revenue Growth: " + fmt(d["rev_growth"], suffix="%", mult=100))
                st.markdown("Div Yield: " + fmt(d["div_yield"], suffix="%", mult=100))
                st.markdown("Market Cap: " + fmt_large(d["mkt_cap"]))

        if col_jyo and j:
            with col_jyo:
                j_pill = signal_pill(j["signal"])
                st.markdown(
                    '<div class="signal-card"><h4>Jyotish</h4>'
                    '<div class="value">' + j_pill +
                    " &nbsp; " + str(j["score"]) + "/100</div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Key Indicators**")
                st.markdown("Moon Nakshatra: **" + j["moon_nakshatra"] + "**")
                st.markdown("Dhana Yogas: **" + str(len(j["dhana_yogas"])) + "** active")
                st.markdown("BNN Score: **" + str(j["bnn_score"]) + "**/10")
                st.markdown("Retrogrades: **" + str(j["retro_count"]) + "**")

                st.markdown("**Planetary Strength**")
                for p in j["planets"]:
                    icon = "🟢" if p["status"] in ["VERY_STRONG", "STRONG"] else "🔴" if p["status"] == "VERY_WEAK" else "⚪"
                    retro_tag = " R" if p["retro"] else ""
                    st.markdown(
                        icon + " " + p["planet"] + " in " +
                        p["sign"] + " " + str(p["degree"]) + "d" +
                        retro_tag
                    )

        # COMBINED VERDICT
        st.markdown('<div class="section-label">Combined Verdict</div>', unsafe_allow_html=True)

        j_score_val = j["score"] if j else None
        score, signal, weights = combined_verdict(
            d["tech_score"], d["fund_score"], j_score_val, use_jyotish
        )

        css_class = "verdict-buy" if score >= 58 else "verdict-sell" if score < 42 else "verdict-hold"
        st.markdown(
            '<div class="verdict-box ' + css_class + '">'
            '<div class="signal-text">' + signal + '</div>'
            '<div class="score-text">Score: ' + str(score) + ' / 100</div>'
            '<div class="weight-text">' + weights + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if use_jyotish and j and j["dhana_yogas"]:
            with st.expander("Jyotish Market Details"):
                st.markdown("**Active Dhana Yogas (Wealth Combinations):**")
                for y in j["dhana_yogas"]:
                    st.markdown(
                        "- **" + y.get("yoga", "Yoga") + "** - " +
                        y.get("description", "") +
                        " | Strength: " + y["strength"]
                    )


# ═══════════════════════════════════════════════════════
# MODE 2: WATCHLIST
# ═══════════════════════════════════════════════════════
elif mode == "Watchlist":
    st.markdown("# Watchlist")

    default_str = ", ".join(DEFAULT_WATCHLIST)
    tickers_input = st.text_area(
        "Enter tickers (comma-separated)",
        default_str,
        height=68,
        placeholder="AAPL, RELIANCE.NS, SPY, BTC-USD...",
    )

    if st.button("Load Watchlist", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        if not tickers:
            st.warning("Enter at least one ticker.")
            st.stop()

        j = None
        if use_jyotish:
            with st.spinner("Calculating Jyotish..."):
                j = calculate_jyotish()

        progress = st.progress(0)
        results = []
        for i, t in enumerate(tickers):
            progress.progress((i + 1) / len(tickers), text="Fetching " + t + "...")
            d = fetch_market_data(t)
            if "error" not in d:
                results.append(d)
        progress.empty()

        if not results:
            st.error("No data found.")
            st.stop()

        if use_jyotish and j:
            st.markdown(
                '<div class="signal-card">'
                '<b>Jyotish Overlay</b> &nbsp; ' +
                signal_pill(j["signal"]) +
                " &nbsp; Score: " + str(j["score"]) + "/100 &nbsp;|&nbsp; "
                "Moon: " + j["moon_nakshatra"] +
                " &nbsp;|&nbsp; Dhana Yogas: " + str(len(j["dhana_yogas"])) +
                " &nbsp;|&nbsp; Retrogrades: " + str(j["retro_count"]) +
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown("")

        hdr = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
        hdr[0].markdown("**Asset**")
        hdr[1].markdown("**Price**")
        hdr[2].markdown("**1D**")
        hdr[3].markdown("**1W**")
        hdr[4].markdown("**1M**")
        hdr[5].markdown("**RSI**")
        hdr[6].markdown("**Technical**")
        hdr[7].markdown("**Verdict**")

        for d in results:
            j_val = j["score"] if j else None
            score, signal, _ = combined_verdict(
                d["tech_score"], d["fund_score"], j_val, use_jyotish
            )

            row = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
            row[0].markdown("**" + d["ticker"] + "**  \n" + d["asset_type"])
            row[1].markdown(d["currency"] + str(d["price"]))

            for idx, chg in [(2, d["chg_1d"]), (3, d["chg_1w"]), (4, d["chg_1m"])]:
                color = "🟢" if chg > 0 else "🔴" if chg < 0 else "⚪"
                row[idx].markdown(color + " " + str(chg) + "%")

            rsi_icon = "🔥" if d["rsi"] > 70 else "💎" if d["rsi"] < 30 else ""
            row[5].markdown(str(d["rsi"]) + " " + rsi_icon)

            row[6].markdown(signal_pill(d["tech_signal"]), unsafe_allow_html=True)
            row[7].markdown(signal_pill(signal), unsafe_allow_html=True)

            st.markdown("<hr style='margin:0; border-color:#1e2530;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# MODE 3: VALIDATE JYOTISH
# ═══════════════════════════════════════════════════════
elif mode == "Validate Jyotish":
    st.markdown("# Validate Jyotish")
    st.markdown(
        "Tests Jyotish signals against **actual historical returns**. "
        "Results may show it adds **no value**."
    )

    col1, col2 = st.columns(2)
    with col1:
        bt_ticker = st.text_input("Ticker", "RELIANCE.NS", key="bt_t")
    with col2:
        bt_months = st.slider("Months of history", 3, 24, 6)

    if st.button("Run Backtest", type="primary"):
        from engines.backtester import MarketBacktester

        with st.spinner("Backtesting " + bt_ticker + "... (2-5 min)"):
            bt = MarketBacktester()
            result = bt.backtest_stock(bt_ticker, bt_months)

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown("---")
            st.markdown("### Results: " + bt_ticker)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Correlation", str(result["correlation"]))
            c2.metric("BUY Accuracy", str(result["buy_accuracy"]) + "%")
            c3.metric("SELL Accuracy", str(result["sell_accuracy"]) + "%")
            c4.metric("Signals", str(result["total_signals"]))

            st.markdown("### Returns")
            r1, r2, r3 = st.columns(3)
            r1.metric("Buy and Hold", str(result["buy_hold_return"]) + "%")
            r2.metric("Jyotish Strategy", str(result["jyotish_strategy_return"]) + "%")
            op = result["jyotish_outperformance"]
            r3.metric("Outperformance", str(op) + "%", delta=str(op) + "%")

            st.markdown("### Component Analysis")
            for comp, corr in result["component_correlations"].items():
                ac = abs(corr)
                tag = "🟢 USEFUL" if ac > 0.15 else "🟡 WEAK" if ac > 0.05 else "🔴 NONE"
                st.markdown(tag + " **" + comp + "**: " + str(corr))

            st.markdown("---")
            v = result["verdict"]
            if v["adds_value"]:
                st.success(
                    "Jyotish adds value for " + bt_ticker +
                    "  \nRecommended weight: **" + str(v["recommended_weight"]) + "%**" +
                    "  \n" + v["honest_assessment"]
                )
            else:
                st.error(
                    "Jyotish does NOT add value for " + bt_ticker +
                    "  \n" + v["honest_assessment"]
                )

            with st.expander("Raw Signal Data"):
                import pandas as pd
                raw_df = pd.DataFrame(result["raw_data"])
                if not raw_df.empty:
                    display_cols = ["date", "jyotish_score", "signal",
                                    "actual_return", "dhana_yogas", "retrogrades"]
                    display_cols = [c for c in display_cols if c in raw_df.columns]
                    st.dataframe(raw_df[display_cols], use_container_width=True)
