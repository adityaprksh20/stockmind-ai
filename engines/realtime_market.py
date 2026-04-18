"""
Real-Time Market Engine
=======================
Enhanced market data fetching with:
- Auto-retry on failure
- Multi-timeframe technicals
- Sector detection
- Currency-aware formatting
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# ── ASSET EXAMPLES (for UI display only — app fetches ANY valid ticker) ──
ASSET_EXAMPLES = {
    "Indian Stocks (NSE)": [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS",
        "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "LT.NS",
        "HINDUNILVR.NS", "BAJFINANCE.NS", "MARUTI.NS", "TATAMOTORS.NS",
        "SUNPHARMA.NS", "ADANIENT.NS", "ASIANPAINT.NS", "TITAN.NS",
        "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NTPC.NS",
        "POWERGRID.NS", "ONGC.NS", "JSWSTEEL.NS", "TATASTEEL.NS",
        "COALINDIA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS",
        "TATACONSUM.NS", "DIVISLAB.NS", "ZOMATO.NS", "PAYTM.NS",
        "NYKAA.NS", "IRCTC.NS", "HAL.NS", "BEL.NS",
    ],
    "Indian Stocks (BSE)": [
        "RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "INFY.BO",
    ],
    "US Stocks": [
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "NVDA", "META",
        "BRK-B", "JPM", "V", "MA", "JNJ", "WMT", "PG", "UNH",
        "HD", "DIS", "NFLX", "PYPL", "AMD", "INTC", "CRM", "ORCL",
        "CSCO", "PEP", "KO", "COST", "ABBV", "MRK", "PFE", "TMO",
        "NKE", "SBUX", "BA", "CAT", "GE", "MMM", "IBM", "GS",
        "MS", "C", "WFC", "AXP", "UBER", "ABNB", "SNAP", "SQ",
        "ROKU", "PLTR", "SOFI", "RIVN", "LCID",
    ],
    "European Stocks": [
        "NESN.SW", "NOVN.SW", "ROG.SW",
        "ASML.AS", "PHIA.AS", "INGA.AS",
        "SAP.DE", "SIE.DE", "ALV.DE", "BAS.DE", "BMW.DE", "MBG.DE", "DTE.DE",
        "MC.PA", "OR.PA", "TTE.PA", "SAN.PA", "AIR.PA", "BNP.PA",
        "SHEL.L", "AZN.L", "ULVR.L", "HSBA.L", "BP.L", "GSK.L", "RIO.L",
        "SAN.MC", "TEF.MC", "ITX.MC",
    ],
    "Asian Stocks": [
        "TSM", "9988.HK", "0700.HK", "9618.HK", "1211.HK",
        "7203.T", "6758.T", "9984.T", "6861.T", "8306.T",
        "005930.KS", "000660.KS", "035420.KS",
        "GRAB", "SE",
    ],
    "Indian ETFs": [
        "NIFTYBEES.NS", "BANKBEES.NS", "GOLDBEES.NS", "SILVERBEES.NS",
        "JUNIORBEES.NS", "ITETF.NS", "CPSE.NS", "LIQUIDBEES.NS",
        "MOM100.NS", "QUAL30IETF.NS",
    ],
    "US ETFs": [
        "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VT",
        "EEM", "EFA", "VWO", "IEMG",
        "XLF", "XLK", "XLE", "XLV", "XLI", "XLP", "XLY", "XLB", "XLU", "XLRE",
        "GLD", "SLV", "USO", "UNG",
        "TLT", "BND", "HYG", "LQD", "AGG",
        "ARKK", "ARKF", "ARKG", "ARKW",
        "SOXX", "SMH", "HACK", "BOTZ", "ROBO",
        "VNQ", "REET",
    ],
    "Global ETFs": [
        "EWJ", "EWG", "EWU", "EWZ", "EWY", "EWT",
        "FXI", "INDA", "INDY",
        "KWEB", "CQQQ",
    ],
    "Commodities": [
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F",
        "ZC=F", "ZW=F", "ZS=F",
        "GLD", "SLV", "USO", "PDBC",
    ],
    "Crypto": [
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
        "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
        "LINK-USD", "UNI-USD", "ATOM-USD", "LTC-USD", "NEAR-USD",
        "APT-USD", "ARB-USD", "OP-USD", "FIL-USD", "AAVE-USD",
    ],
    "Currencies (Forex)": [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
        "AUDUSD=X", "USDCAD=X", "USDINR=X", "USDCNY=X",
        "GBPINR=X", "EURINR=X", "JPYINR=X",
    ],
    "Indices": [
        "^NSEI", "^BSESN", "^NSEBANK",
        "^GSPC", "^DJI", "^IXIC", "^RUT",
        "^FTSE", "^GDAXI", "^FCHI", "^N225", "^HSI",
        "^VIX",
    ],
    "Bonds / Rates": [
        "^TNX", "^TYX", "^FVX", "^IRX",
        "TLT", "IEF", "SHY", "BND",
    ],
}

# ── TICKER FORMAT GUIDE (shown in UI) ──
TICKER_FORMAT_GUIDE = {
    "NSE India": "Add .NS (e.g. RELIANCE.NS, TCS.NS)",
    "BSE India": "Add .BO (e.g. RELIANCE.BO, TCS.BO)",
    "US Stocks": "Plain symbol (e.g. AAPL, MSFT, TSLA)",
    "London": "Add .L (e.g. SHEL.L, AZN.L)",
    "Germany": "Add .DE (e.g. SAP.DE, BMW.DE)",
    "France": "Add .PA (e.g. MC.PA, TTE.PA)",
    "Japan": "Add .T (e.g. 7203.T for Toyota)",
    "Hong Kong": "Add .HK (e.g. 0700.HK for Tencent)",
    "Korea": "Add .KS (e.g. 005930.KS for Samsung)",
    "Switzerland": "Add .SW (e.g. NESN.SW for Nestle)",
    "Canada": "Add .TO (e.g. SHOP.TO for Shopify)",
    "Australia": "Add .AX (e.g. BHP.AX, CBA.AX)",
    "Crypto": "Add -USD (e.g. BTC-USD, ETH-USD)",
    "Forex": "Add =X (e.g. USDINR=X, EURUSD=X)",
    "Futures": "Add =F (e.g. GC=F for Gold, CL=F for Oil)",
    "Indices": "Prefix ^ (e.g. ^NSEI, ^GSPC, ^VIX)",
}

DEFAULT_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "AAPL", "MSFT", "NVDA", "SPY", "QQQ", "GLD", "BTC-USD"]


def get_currency_symbol(info):
    cur = info.get("currency", "USD")
    return {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}.get(cur, cur + " ")


def detect_asset_type(ticker, info):
    qt = info.get("quoteType", "").upper()
    if qt == "ETF": return "ETF"
    if qt == "MUTUALFUND": return "Mutual Fund"
    if qt == "CRYPTOCURRENCY": return "Crypto"
    if ".NS" in ticker or ".BO" in ticker: return "Indian Stock"
    return "Stock"


def safe_div(a, b):
    if b is None or b == 0: return 0
    if a is None: return 0
    return a / b


def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace(0, float('nan'))
    rsi = 100 - (100 / (1 + rs))
    return rsi


def fetch_market_data(ticker):
    """Fetch comprehensive market data for any global asset."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        # Try 1y first, fall back to 6mo
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 2:
            hist = stock.history(period="6mo")
        if hist.empty or len(hist) < 2:
            hist = stock.history(period="3mo")
        if hist.empty or len(hist) < 2:
            return {"error": "No price data for " + ticker}

        close = hist["Close"]
        price = round(close.iloc[-1], 2)
        cur = get_currency_symbol(info)
        atype = detect_asset_type(ticker, info)

        # ── RETURNS ──
        def safe_return(n):
            if len(close) > n:
                return round((close.iloc[-1] / close.iloc[-n] - 1) * 100, 2)
            return 0.0

        chg_1d = safe_return(2)
        chg_1w = safe_return(6)
        chg_1m = safe_return(22)
        chg_3m = safe_return(63)
        chg_6m = safe_return(126)
        chg_1y = round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2)

        # ── TECHNICALS ──
        sma_20 = round(close.tail(20).mean(), 2)
        sma_50 = round(close.tail(50).mean(), 2) if len(close) >= 50 else None
        sma_200 = round(close.tail(200).mean(), 2) if len(close) >= 200 else None

        ema_12 = round(close.ewm(span=12, adjust=False).mean().iloc[-1], 2)
        ema_26 = round(close.ewm(span=26, adjust=False).mean().iloc[-1], 2)
        macd_line = round(ema_12 - ema_26, 2)
        macd_signal = round(
            (close.ewm(span=12, adjust=False).mean() -
             close.ewm(span=26, adjust=False).mean())
            .ewm(span=9, adjust=False).mean().iloc[-1], 2
        )
        macd_histogram = round(macd_line - macd_signal, 2)

        rsi_series = compute_rsi(close, 14)
        rsi = round(rsi_series.iloc[-1], 1) if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0

        # Bollinger Bands
        bb_mid = sma_20
        bb_std = round(close.tail(20).std(), 2)
        bb_upper = round(bb_mid + 2 * bb_std, 2)
        bb_lower = round(bb_mid - 2 * bb_std, 2)

        # ATR (14-period)
        high = hist["High"]
        low = hist["Low"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = round(tr.tail(14).mean(), 2)
        atr_pct = round(atr / price * 100, 2)

        # Volume
        vol_today = int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
        vol_avg = int(hist["Volume"].tail(20).mean()) if "Volume" in hist.columns else 1
        vol_ratio = round(safe_div(vol_today, vol_avg), 1)

        # 52W
        high_52w = round(close.max(), 2)
        low_52w = round(close.min(), 2)
        from_high = round((price / high_52w - 1) * 100, 1) if high_52w > 0 else 0

        # ── TECHNICAL SCORE ──
        t_score = 0
        if price > sma_20: t_score += 1
        else: t_score -= 1
        if sma_50 and price > sma_50: t_score += 1
        elif sma_50: t_score -= 1
        if sma_50 and sma_20 > sma_50: t_score += 1
        elif sma_50: t_score -= 1
        if sma_200 and price > sma_200: t_score += 1
        elif sma_200: t_score -= 1
        if macd_line > 0: t_score += 1
        else: t_score -= 1
        if macd_histogram > 0: t_score += 1
        else: t_score -= 1
        if rsi < 30: t_score += 1
        elif rsi > 70: t_score -= 1
        if price < bb_lower: t_score += 1
        elif price > bb_upper: t_score -= 1
        if vol_ratio > 1.5 and chg_1d > 0: t_score += 1
        elif vol_ratio > 1.5 and chg_1d < 0: t_score -= 1

        tech_signal = "BULLISH" if t_score >= 4 else "BEARISH" if t_score <= -4 else "NEUTRAL"
        tech_score = max(0, min(100, 50 + t_score * 6))

        # ── FUNDAMENTALS ──
        pe = info.get("trailingPE")
        fwd_pe = info.get("forwardPE")
        pb = info.get("priceToBook")
        ps = info.get("priceToSalesTrailing12Months")
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")
        debt_eq = info.get("debtToEquity")
        div_yield = info.get("dividendYield")
        mkt_cap = info.get("marketCap")
        rev_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        sector = info.get("sector", "-")
        industry = info.get("industry", "-")
        name = info.get("shortName", ticker)

        # ETF fields
        expense_ratio = info.get("annualReportExpenseRatio")
        nav = info.get("navPrice")
        total_assets = info.get("totalAssets")
        ytd_return = info.get("ytdReturn")
        three_yr = info.get("threeYearAverageReturn")
        five_yr = info.get("fiveYearAverageReturn")

        # ── FUNDAMENTAL SCORE ──
        f_score = 0
        if pe and pe < 20: f_score += 2
        elif pe and pe < 30: f_score += 1
        elif pe and pe > 50: f_score -= 2
        elif pe and pe > 35: f_score -= 1
        if roe and roe > 0.20: f_score += 2
        elif roe and roe > 0.12: f_score += 1
        elif roe and roe < 0.05: f_score -= 1
        if debt_eq is not None and debt_eq < 50: f_score += 2
        elif debt_eq is not None and debt_eq < 100: f_score += 1
        elif debt_eq is not None and debt_eq > 200: f_score -= 2
        if rev_growth and rev_growth > 0.15: f_score += 1
        if earnings_growth and earnings_growth > 0.15: f_score += 1
        if profit_margin and profit_margin > 0.20: f_score += 1
        elif profit_margin and profit_margin < 0.05: f_score -= 1
        if div_yield and div_yield > 0.02: f_score += 1

        fund_signal = "BULLISH" if f_score >= 4 else "BEARISH" if f_score <= -2 else "NEUTRAL"
        fund_score = max(0, min(100, 50 + f_score * 6))

        return {
            "ticker": ticker, "name": name, "asset_type": atype,
            "currency": cur, "sector": sector, "industry": industry,
            "price": price,
            "chg_1d": chg_1d, "chg_1w": chg_1w, "chg_1m": chg_1m,
            "chg_3m": chg_3m, "chg_6m": chg_6m, "chg_1y": chg_1y,
            "high_52w": high_52w, "low_52w": low_52w, "from_high": from_high,
            "sma_20": sma_20, "sma_50": sma_50, "sma_200": sma_200,
            "ema_12": ema_12, "ema_26": ema_26,
            "macd_line": macd_line, "macd_signal": macd_signal,
            "macd_histogram": macd_histogram,
            "rsi": rsi,
            "bb_upper": bb_upper, "bb_mid": bb_mid, "bb_lower": bb_lower,
            "atr": atr, "atr_pct": atr_pct,
            "vol_today": vol_today, "vol_avg": vol_avg, "vol_ratio": vol_ratio,
            "tech_signal": tech_signal, "tech_score": tech_score,
            "pe": pe, "fwd_pe": fwd_pe, "pb": pb, "ps": ps,
            "roe": roe, "roa": roa, "debt_eq": debt_eq,
            "div_yield": div_yield, "mkt_cap": mkt_cap,
            "rev_growth": rev_growth, "earnings_growth": earnings_growth,
            "profit_margin": profit_margin,
            "fund_signal": fund_signal, "fund_score": fund_score,
            "expense_ratio": expense_ratio, "nav": nav,
            "total_assets": total_assets, "ytd_return": ytd_return,
            "three_yr_return": three_yr, "five_yr_return": five_yr,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        return {"error": str(e)}


def fmt(val, suffix="", prefix="", mult=1, decimals=1):
    if val is None: return "-"
    return prefix + str(round(val * mult, decimals)) + suffix


def fmt_large(val):
    if val is None: return "-"
    if val >= 1e12: return str(round(val / 1e12, 2)) + "T"
    if val >= 1e9: return str(round(val / 1e9, 2)) + "B"
    if val >= 1e7: return str(round(val / 1e7, 2)) + "Cr"
    if val >= 1e5: return str(round(val / 1e5, 2)) + "L"
    return str(val)


def chg_arrow(val):
    if val > 0: return "+" + str(val) + "%"
    if val < 0: return str(val) + "%"
    return "0%"
