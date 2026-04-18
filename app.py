import streamlit as st
import os

st.set_page_config(page_title="StockMind AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)

from datetime import datetime
from engines.realtime_market import (
    fetch_market_data, fmt, fmt_large, chg_arrow,
    ASSET_EXAMPLES, DEFAULT_WATCHLIST, TICKER_FORMAT_GUIDE,
)


with st.sidebar:
    st.markdown("## StockMind AI")
    st.caption("Global Market Intelligence + Vedic Astrology")
    st.markdown("---")
    use_jyotish = st.toggle("Vedic Jyotish Layer", value=False)
    if use_jyotish:
        st.caption("4-signal Jyotish engine active")
    else:
        st.caption("Pure fundamentals + technicals")
    st.markdown("---")
    modes = ["Analyze", "Watchlist"]
    if use_jyotish:
        modes.extend(["Sector Rotation", "Cosmic Events", "Validate"])
    mode = st.radio("Mode", modes, label_visibility="collapsed")
    st.markdown("---")
    with st.expander("Ticker Format Guide"):
        st.markdown("**Type any valid ticker. Here are the formats:**")
        for market, hint in TICKER_FORMAT_GUIDE.items():
            st.markdown("**" + market + ":** " + hint)
    with st.expander("Example Tickers"):
        for cat, tks in ASSET_EXAMPLES.items():
            st.markdown("**" + cat + "**")
            st.caption(", ".join(tks[:8]) + (" ..." if len(tks) > 8 else ""))
    st.markdown('<div class="disclaimer-box">Not financial advice. Jyotish signals are experimental and must be validated.</div>', unsafe_allow_html=True)


def pill(signal):
    colors = {
        "BULLISH": "pill-green", "STRONG_BUY": "pill-green", "BUY": "pill-green",
        "OVERWEIGHT": "pill-green", "SLIGHT_OW": "pill-green",
        "VERY_FAVORABLE": "pill-green", "FAVORABLE": "pill-green",
        "BEARISH": "pill-red", "STRONG_SELL": "pill-red", "SELL": "pill-red",
        "UNDERWEIGHT": "pill-red", "HIGH_RISK": "pill-red", "CAUTION": "pill-red",
        "NEUTRAL": "pill-yellow", "HOLD": "pill-yellow", "SLIGHT_UW": "pill-yellow",
    }
    css = colors.get(signal, "pill-blue")
    return "<span class=\"pill " + css + "\">" + signal + "</span>"


def verdict_calc(tech, fund, jyo=None, use_j=False):
    if use_j and jyo is not None:
        wt, wf, wj = 0.25, 0.40, 0.35
        s = round(tech * wt + fund * wf + jyo * wj, 1)
        w = "Tech " + str(int(wt*100)) + "% | Fund " + str(int(wf*100)) + "% | Jyotish " + str(int(wj*100)) + "%"
    else:
        wt, wf = 0.40, 0.60
        s = round(tech * wt + fund * wf, 1)
        w = "Tech " + str(int(wt*100)) + "% | Fund " + str(int(wf*100)) + "%"
    sig = "STRONG BUY" if s >= 72 else "BUY" if s >= 58 else "HOLD" if s >= 42 else "SELL" if s >= 28 else "STRONG SELL"
    return s, sig, w


if mode == "Analyze":
    st.markdown("# Analyze")
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        ticker = st.text_input("Any global ticker", "RELIANCE.NS", placeholder="AAPL, TCS.NS, SPY, BTC-USD, USDINR=X, GC=F, ^VIX...")
    with c2:
        horizon = st.selectbox("Horizon", ["1 Week", "1 Month", "3 Months", "1 Year"])
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Analyze", type="primary", use_container_width=True)

    if run and ticker.strip():
        ticker = ticker.strip().upper()
        with st.spinner("Fetching market data..."):
            d = fetch_market_data(ticker)
        if "error" in d:
            st.error(d["error"])
            st.stop()

        j = None
        if use_jyotish:
            with st.spinner("Computing Jyotish signals..."):
                from engines.signal_scorer import SignalScorer
                j = SignalScorer().get_full_score(ticker)

        st.markdown("---")
        st.markdown("### " + d["name"] + " &nbsp;" + pill(d["asset_type"]), unsafe_allow_html=True)
        st.caption("Fetched: " + d.get("fetched_at", "") + " | " + d["sector"] + " | " + d.get("industry", ""))

        h1, h2, h3, h4, h5, h6 = st.columns(6)
        h1.metric("Price", d["currency"] + str(d["price"]), str(d["chg_1d"]) + "%")
        h2.metric("1W", chg_arrow(d["chg_1w"]))
        h3.metric("1M", chg_arrow(d["chg_1m"]))
        h4.metric("3M", chg_arrow(d["chg_3m"]))
        h5.metric("1Y", chg_arrow(d["chg_1y"]))
        h6.metric("From 52W High", str(d["from_high"]) + "%")

        st.markdown("<div class=\"section-label\">Signal Breakdown</div>", unsafe_allow_html=True)

        if use_jyotish and j:
            col_t, col_f, col_j = st.columns(3)
        else:
            col_t, col_f = st.columns(2)
            col_j = None

        with col_t:
            st.markdown("<div class=\"signal-card\"><h4>Technical</h4><div class=\"value\">" + pill(d["tech_signal"]) + " &nbsp;" + str(d["tech_score"]) + "/100</div></div>", unsafe_allow_html=True)
            st.markdown("**Trend**")
            st.markdown("SMA 20: " + d["currency"] + str(d["sma_20"]) + (" ✅" if d["price"] > d["sma_20"] else " ⚠️"))
            if d["sma_50"]:
                st.markdown("SMA 50: " + d["currency"] + str(d["sma_50"]) + (" ✅" if d["price"] > d["sma_50"] else " ⚠️"))
            if d["sma_200"]:
                st.markdown("SMA 200: " + d["currency"] + str(d["sma_200"]) + (" ✅" if d["price"] > d["sma_200"] else " ⚠️"))
            st.markdown("**Momentum**")
            rsi_t = " Overbought" if d["rsi"] > 70 else " Oversold" if d["rsi"] < 30 else ""
            st.markdown("RSI: " + str(d["rsi"]) + rsi_t)
            st.markdown("MACD: " + str(d["macd_line"]) + " (Signal: " + str(d["macd_signal"]) + ")")
            st.markdown("Histogram: " + str(d["macd_histogram"]) + (" ✅" if d["macd_histogram"] > 0 else " ⚠️"))
            st.markdown("**Volatility**")
            st.markdown("Bollinger: " + d["currency"] + str(d["bb_lower"]) + " - " + d["currency"] + str(d["bb_upper"]))
            st.markdown("ATR: " + str(d["atr"]) + " (" + str(d["atr_pct"]) + "%)")
            st.markdown("Volume: " + str(d["vol_ratio"]) + "x avg")

        with col_f:
            st.markdown("<div class=\"signal-card\"><h4>Fundamental</h4><div class=\"value\">" + pill(d["fund_signal"]) + " &nbsp;" + str(d["fund_score"]) + "/100</div></div>", unsafe_allow_html=True)
            if d["asset_type"] in ["ETF", "Mutual Fund"]:
                st.markdown("**Fund Metrics**")
                st.markdown("NAV: " + fmt(d["nav"], prefix=d["currency"]))
                st.markdown("Expense: " + fmt(d["expense_ratio"], suffix="%", mult=100))
                st.markdown("Assets: " + fmt_large(d["total_assets"]))
                st.markdown("YTD: " + fmt(d["ytd_return"], suffix="%", mult=100))
                st.markdown("3Y: " + fmt(d["three_yr_return"], suffix="%", mult=100))
                st.markdown("5Y: " + fmt(d["five_yr_return"], suffix="%", mult=100))
            else:
                st.markdown("**Valuation**")
                pe_str = fmt(d["pe"])
                if d["pe"]:
                    pe_str += " ✅" if d["pe"] < 25 else (" ⚠️" if d["pe"] > 40 else "")
                st.markdown("P/E: " + pe_str)
                st.markdown("Fwd P/E: " + fmt(d["fwd_pe"]))
                st.markdown("P/B: " + fmt(d["pb"]) + " | P/S: " + fmt(d["ps"]))
                st.markdown("**Quality**")
                roe_str = fmt(d["roe"], suffix="%", mult=100)
                if d["roe"] and d["roe"] > 0.15:
                    roe_str += " ✅"
                st.markdown("ROE: " + roe_str)
                st.markdown("ROA: " + fmt(d["roa"], suffix="%", mult=100))
                st.markdown("Margin: " + fmt(d["profit_margin"], suffix="%", mult=100))
                de_str = fmt(d["debt_eq"])
                if d["debt_eq"] is not None:
                    de_str += " ✅" if d["debt_eq"] < 100 else (" ⚠️" if d["debt_eq"] > 200 else "")
                st.markdown("D/E: " + de_str)
                st.markdown("**Growth**")
                st.markdown("Revenue: " + fmt(d["rev_growth"], suffix="%", mult=100))
                st.markdown("Earnings: " + fmt(d["earnings_growth"], suffix="%", mult=100))
                st.markdown("Div Yield: " + fmt(d["div_yield"], suffix="%", mult=100))
                st.markdown("Mkt Cap: " + fmt_large(d["mkt_cap"]))

        if col_j and j:
            with col_j:
                st.markdown("<div class=\"signal-card\"><h4>Jyotish (4-Signal)</h4><div class=\"value\">" + pill(j["signal"]) + " &nbsp;" + str(j["combined_score"]) + "/100</div></div>", unsafe_allow_html=True)
                sky = j["sky_snapshot"]
                st.markdown("**Composite Scores**")
                for key, label in [("general_jyotish", "General"), ("company_transit", "Company Chart"), ("sector_karaka", "Sector Karaka"), ("events", "Events")]:
                    sc = j["scores"].get(key, 50)
                    wt = j["weights"].get(key, 0)
                    wt_pct = str(int(wt * 100)) + "%"
                    icon = "🟢" if sc >= 60 else "🔴" if sc < 40 else "🟡"
                    st.markdown(icon + " " + label + ": **" + str(sc) + "** (" + wt_pct + " weight)")
                st.markdown("**Sky Now**")
                st.markdown("Moon: **" + sky["moon_nakshatra"] + "** in " + sky["moon_sign"])
                st.markdown("Phase: " + sky["moon_phase"])
                st.markdown("Market Bias: **" + sky["market_bias"] + "**")
                st.markdown("Tithi: " + str(sky["tithi"]))
                if sky["retrogrades"]:
                    st.markdown("Retro: **" + ", ".join(sky["retrogrades"]) + "**")
                else:
                    st.markdown("No retrogrades ✅")
                if sky["eclipse_soon"]:
                    st.markdown("**Eclipse approaching** ⚠️")
                st.markdown("Dhana Yogas: **" + str(len(j["dhana_yogas"])) + "** | BNN: **" + str(j["bnn_score"]) + "**/10")

        st.markdown("<div class=\"section-label\">Combined Verdict</div>", unsafe_allow_html=True)
        jsc = j["combined_score"] if j else None
        score, sig, wts = verdict_calc(d["tech_score"], d["fund_score"], jsc, use_jyotish)
        css = "verdict-buy" if score >= 58 else "verdict-sell" if score < 42 else "verdict-hold"
        verdict_html = (
            "<div class=\"verdict-box " + css + "\">"
            "<div class=\"signal-text\">" + sig + "</div>"
            "<div class=\"score-text\">Score: " + str(score) + " / 100</div>"
            "<div class=\"weight-text\">" + wts + "</div>"
            "</div>"
        )
        st.markdown(verdict_html, unsafe_allow_html=True)

        if use_jyotish and j:
            with st.expander("Planetary Positions (Real-Time Sidereal)"):
                for p, data in j["positions"].items():
                    retro = " R" if data["retrograde"] else ""
                    st.markdown("**" + p + "** " + data["sign"] + " " + str(data["degree"]) + "° " + data["nakshatra"] + retro)

            ct = j.get("details", {}).get("company_transit", {})
            if ct.get("available") is not False and ct.get("top_positive"):
                with st.expander("Company Birth Chart Transits"):
                    st.markdown("**Birth:** " + ct.get("birth_date", "-") + " | **Lagna:** " + ct.get("lagna", "-"))
                    if ct.get("top_positive"):
                        st.markdown("**Favorable:**")
                        for t in ct["top_positive"]:
                            st.markdown("✅ " + t["planet"] + " in House " + str(t["transit_house"]) + " - " + t["interpretation"])
                    if ct.get("top_negative"):
                        st.markdown("**Challenging:**")
                        for t in ct["top_negative"]:
                            st.markdown("⚠️ " + t["planet"] + " in House " + str(t["transit_house"]) + " - " + t["interpretation"])

            if j["dhana_yogas"]:
                with st.expander("Dhana Yogas (Wealth Combinations)"):
                    for y in j["dhana_yogas"]:
                        st.markdown("- **" + y.get("yoga", "") + "** - " + y.get("description", "") + " | " + y["strength"])

            ed = j.get("details", {}).get("events", {})
            if ed.get("conjunctions"):
                with st.expander("Active Conjunctions"):
                    for c in ed["conjunctions"]:
                        st.markdown("**" + c["planet1"] + " + " + c["planet2"] + "** in " + c.get("sign", "") + " (" + str(c["degree_separation"]) + "° apart)")


elif mode == "Watchlist":
    st.markdown("# Watchlist")
    tickers_input = st.text_area(
        "Tickers (comma-separated) - any global stock, ETF, crypto, forex, index",
        ", ".join(DEFAULT_WATCHLIST),
        height=80,
        placeholder="AAPL, RELIANCE.NS, BTC-USD, USDINR=X, ^NSEI, GC=F, SPY..."
    )
    if st.button("Load", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        if not tickers:
            st.warning("Enter at least one ticker.")
            st.stop()
        j = None
        if use_jyotish:
            with st.spinner("Jyotish..."):
                from engines.signal_scorer import SignalScorer
                j = SignalScorer().get_full_score(tickers[0])
        prog = st.progress(0)
        results = []
        for i, t in enumerate(tickers):
            prog.progress((i+1)/len(tickers), text=t)
            d = fetch_market_data(t)
            if "error" not in d:
                results.append(d)
        prog.empty()
        if not results:
            st.error("No data.")
            st.stop()
        if use_jyotish and j:
            sky = j["sky_snapshot"]
            st.markdown("<div class=\"signal-card\"><b>Jyotish</b> " + pill(j["signal"]) + " Score: " + str(j["combined_score"]) + " | Moon: " + sky["moon_nakshatra"] + " | Bias: " + sky["market_bias"] + " | Retro: " + str(sky["retrograde_count"]) + "</div>", unsafe_allow_html=True)
        hdr = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
        for i, l in enumerate(["Asset", "Price", "1D", "1W", "1M", "RSI", "Technical", "Verdict"]):
            hdr[i].markdown("**" + l + "**")
        for d in results:
            jsc = j["combined_score"] if j else None
            s, sig, _ = verdict_calc(d["tech_score"], d["fund_score"], jsc, use_jyotish)
            row = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
            row[0].markdown("**" + d["ticker"] + "**  \n" + d["asset_type"])
            row[1].markdown(d["currency"] + str(d["price"]))
            for idx, chg in [(2, d["chg_1d"]), (3, d["chg_1w"]), (4, d["chg_1m"])]:
                c = "🟢" if chg > 0 else "🔴" if chg < 0 else "⚪"
                row[idx].markdown(c + " " + str(chg) + "%")
            row[5].markdown(str(d["rsi"]))
            row[6].markdown(pill(d["tech_signal"]), unsafe_allow_html=True)
            row[7].markdown(pill(sig), unsafe_allow_html=True)
            st.markdown("<hr style=\"margin:0;border-color:#1e2530\">", unsafe_allow_html=True)


elif mode == "Sector Rotation":
    st.markdown("# Sector Rotation")
    st.markdown("Sectors favored/unfavored based on planetary karaka strength")
    if st.button("Calculate", type="primary"):
        with st.spinner("Analyzing..."):
            from engines.sector_karaka import SectorKarakaEngine
            result = SectorKarakaEngine().get_sector_signals()
        st.markdown("---")
        for s in result["all_signals"]:
            icon = "🟢" if s["strength_score"] >= 4 else "🔴" if s["strength_score"] <= -4 else "🟡"
            retro = " R" if s["retrograde"] else ""
            st.markdown(icon + " **" + s["planet"] + "** in " + s["sign"] + retro + " - " + pill(s["signal"]), unsafe_allow_html=True)
            st.caption("Sectors: " + ", ".join(s["sectors"]) + " | India: " + ", ".join(s["tickers_india"][:3]) + " | US: " + ", ".join(s["tickers_us"][:3]))
            st.markdown("")


elif mode == "Cosmic Events":
    st.markdown("# Cosmic Events")
    st.markdown("Active astronomical events and their market impact")
    if st.button("Scan Sky", type="primary"):
        with st.spinner("Scanning..."):
            from engines.realtime_astro import RealtimeAstroEngine
            astro = RealtimeAstroEngine()
            snapshot = astro.get_complete_snapshot()
        st.markdown("---")
        moon = snapshot["moon_phase"]
        st.markdown("### Moon Phase")
        st.markdown("**" + moon["moon_nakshatra"] + "** in " + moon["moon_sign"] + " (" + str(moon["moon_degree"]) + "°)")
        st.markdown("Phase: " + moon["phase"])
        st.markdown("Market Bias: **" + moon["market_bias"] + "**")
        st.markdown("Tithi: " + str(moon["tithi"]))

        st.markdown("### Retrogrades")
        if snapshot["retrogrades"]:
            for r in snapshot["retrogrades"]:
                st.markdown("🔄 **" + r["planet"] + "** in " + r["sign"] + " " + str(r["degree"]) + "° (speed: " + str(r["speed"]) + ")")
        else:
            st.markdown("No retrogrades ✅")

        st.markdown("### Conjunctions")
        if snapshot["conjunctions"]:
            for c in snapshot["conjunctions"]:
                tight = "TIGHT" if c["tight"] else "wide"
                st.markdown("**" + c["planet1"] + " + " + c["planet2"] + "** in " + c["sign"] + " (" + str(c["degree_separation"]) + "° - " + tight + ")")
        else:
            st.markdown("No major conjunctions")

        st.markdown("### Upcoming Eclipses")
        if snapshot["upcoming_eclipses"]:
            for e in snapshot["upcoming_eclipses"]:
                st.markdown("🌑 " + e["type"] + " eclipse on **" + e["date"] + "** in " + e["sign"] + " (" + str(e["days_away"]) + " days away)")
        else:
            st.markdown("No eclipses in next 60 days ✅")

        st.markdown("### All Positions")
        for p, data in snapshot["positions"].items():
            retro = " R" if data["retrograde"] else ""
            st.markdown("**" + p + "** " + data["sign"] + " " + str(data["degree"]) + "° " + data["nakshatra"] + " (Pada " + str(data["pada"]) + ")" + retro)


elif mode == "Validate":
    st.markdown("# Validate Jyotish")
    st.markdown("Backtest Jyotish signals against actual returns")
    col1, col2 = st.columns(2)
    with col1:
        bt_ticker = st.text_input("Ticker", "RELIANCE.NS", key="bt_t")
    with col2:
        bt_months = st.slider("Months", 3, 24, 6)
    if st.button("Run Backtest", type="primary"):
        from engines.backtester import MarketBacktester
        with st.spinner("Backtesting... (2-5 min)"):
            bt = MarketBacktester()
            result = bt.backtest_stock(bt_ticker, bt_months)
        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Correlation", str(result["correlation"]))
            c2.metric("BUY Accuracy", str(result["buy_accuracy"]) + "%")
            c3.metric("SELL Accuracy", str(result["sell_accuracy"]) + "%")
            c4.metric("Signals", str(result["total_signals"]))
            r1, r2, r3 = st.columns(3)
            r1.metric("Buy Hold", str(result["buy_hold_return"]) + "%")
            r2.metric("Jyotish Strategy", str(result["jyotish_strategy_return"]) + "%")
            op = result["jyotish_outperformance"]
            r3.metric("Outperformance", str(op) + "%", delta=str(op) + "%")
            st.markdown("### Components")
            for comp, corr in result["component_correlations"].items():
                tag = "🟢" if abs(corr) > 0.15 else "🟡" if abs(corr) > 0.05 else "🔴"
                st.markdown(tag + " **" + comp + "**: " + str(corr))
            st.markdown("---")
            v = result["verdict"]
            if v["adds_value"]:
                st.success("Jyotish adds value. Weight: **" + str(v["recommended_weight"]) + "%**\n\n" + v["honest_assessment"])
            else:
                st.error("Jyotish does NOT add value.\n\n" + v["honest_assessment"])
