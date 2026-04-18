"""
Market Engine - shared data fetching + technical calculations.
Supports: Global stocks, ETFs, Mutual Funds, Crypto.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


ASSET_EXAMPLES = {
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"],
    "US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
    "Global Stocks": ["NESN.SW", "ASML.AS", "TSM", "SAP.DE", "SHOP.TO"],
    "ETFs": ["SPY", "QQQ", "VTI", "EEM", "NIFTYBEES.NS", "GOLDBEES.NS"],
    "Mutual Funds": ["0P0000XVAP.BO", "0P0001BAQ1.BO"],
    "Crypto": ["BTC-USD", "ETH-USD"],
}

DEFAULT_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "AAPL", "MSFT", "SPY", "GOLDBEES.NS"]


def detect_asset_type(ticker, info):
    qt = info.get("quoteType", "").upper()
    if qt == "ETF":
        return "ETF"
    if qt == "MUTUALFUND":
        return "Mutual Fund"
    if qt == "CRYPTOCURRENCY":
        return "Crypto"
    if ".NS" in ticker or ".BO" in ticker:
        return "Indian Stock"
    return "Stock"


def get_currency_symbol(info):
    cur = info.get("currency", "USD")
    symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CHF": "CHF "}
    return symbols.get(cur, cur + " ")


def fetch_market_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        if hist.empty or len(hist) < 5:
            return {"error": "No data found for " + ticker}

        close = hist["Close"]
        price = round(close.iloc[-1], 2)
        cur = get_currency_symbol(info)
        asset_type = detect_asset_type(ticker, info)

        chg_1d = round((close.iloc[-1] / close.iloc[-2] - 1) * 100, 2) if len(close) > 1 else 0
        chg_1w = round((close.iloc[-1] / close.iloc[-6] - 1) * 100, 2) if len(close) > 5 else 0
        chg_1m = round((close.iloc[-1] / close.iloc[-22] - 1) * 100, 2) if len(close) > 21 else 0
        chg_3m = round((close.iloc[-1] / close.iloc[-63] - 1) * 100, 2) if len(close) > 62 else 0
        chg_1y = round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2)

        sma_20 = round(close.tail(20).mean(), 2)
        sma_50 = round(close.tail(50).mean(), 2)
        sma_200 = round(close.tail(200).mean(), 2) if len(close) >= 200 else None
        ema_12 = round(close.ewm(span=12).mean().iloc[-1], 2)
        ema_26 = round(close.ewm(span=26).mean().iloc[-1], 2)
        macd = round(ema_12 - ema_26, 2)

        delta = close.diff()
        gain = delta.where(delta > 0, 0).tail(14).mean()
        loss = -delta.where(delta < 0, 0).tail(14).mean()
        rs = gain / loss if loss != 0 else 100
        rsi = round(100 - (100 / (1 + rs)), 1)

        bb_mid = sma_20
        bb_std = round(close.tail(20).std(), 2)
        bb_upper = round(bb_mid + 2 * bb_std, 2)
        bb_lower = round(bb_mid - 2 * bb_std, 2)

        vol_avg_20 = int(hist["Volume"].tail(20).mean()) if "Volume" in hist else 0
        vol_today = int(hist["Volume"].iloc[-1]) if "Volume" in hist else 0

        high_52w = round(close.max(), 2)
        low_52w = round(close.min(), 2)
        from_high = round((price / high_52w - 1) * 100, 1)

        t_score = 0
        if price > sma_20: t_score += 1
        else: t_score -= 1
        if price > sma_50: t_score += 1
        else: t_score -= 1
        if sma_20 > sma_50: t_score += 1
        else: t_score -= 1
        if sma_200 and price > sma_200: t_score += 1
        elif sma_200: t_score -= 1
        if macd > 0: t_score += 1
        else: t_score -= 1
        if 40 <= rsi <= 60: t_score += 0
        elif rsi < 30: t_score += 1
        elif rsi > 70: t_score -= 1
        if price < bb_lower: t_score += 1
        elif price > bb_upper: t_score -= 1

        tech_signal = "BULLISH" if t_score >= 3 else "BEARISH" if t_score <= -3 else "NEUTRAL"
        tech_score = max(0, min(100, 50 + t_score * 8))

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
        profit_margin = info.get("profitMargins")
        sector = info.get("sector", "-")
        name = info.get("shortName", ticker)

        expense_ratio = info.get("annualReportExpenseRatio")
        nav = info.get("navPrice")
        total_assets = info.get("totalAssets")
        ytd_return = info.get("ytdReturn")
        three_yr_return = info.get("threeYearAverageReturn")
        five_yr_return = info.get("fiveYearAverageReturn")

        f_score = 0
        if pe and pe < 25: f_score += 1
        if pe and pe > 40: f_score -= 1
        if roe and roe > 0.15: f_score += 1
        if roe and roe < 0.05: f_score -= 1
        if debt_eq is not None and debt_eq < 100: f_score += 1
        if debt_eq is not None and debt_eq > 200: f_score -= 1
        if rev_growth and rev_growth > 0.10: f_score += 1
        if profit_margin and profit_margin > 0.15: f_score += 1
        if div_yield and div_yield > 0.02: f_score += 1

        fund_signal = "BULLISH" if f_score >= 3 else "BEARISH" if f_score <= -1 else "NEUTRAL"
        fund_score = max(0, min(100, 50 + f_score * 8))

        return {
            "ticker": ticker, "name": name, "asset_type": asset_type,
            "currency": cur, "sector": sector, "price": price,
            "chg_1d": chg_1d, "chg_1w": chg_1w, "chg_1m": chg_1m,
            "chg_3m": chg_3m, "chg_1y": chg_1y,
            "high_52w": high_52w, "low_52w": low_52w, "from_high": from_high,
            "sma_20": sma_20, "sma_50": sma_50, "sma_200": sma_200,
            "ema_12": ema_12, "ema_26": ema_26, "macd": macd,
            "rsi": rsi, "bb_upper": bb_upper, "bb_lower": bb_lower, "bb_mid": bb_mid,
            "vol_avg": vol_avg_20, "vol_today": vol_today,
            "tech_signal": tech_signal, "tech_score": tech_score,
            "pe": pe, "fwd_pe": fwd_pe, "pb": pb, "ps": ps,
            "roe": roe, "roa": roa, "debt_eq": debt_eq, "div_yield": div_yield,
            "mkt_cap": mkt_cap, "rev_growth": rev_growth,
            "profit_margin": profit_margin,
            "fund_signal": fund_signal, "fund_score": fund_score,
            "expense_ratio": expense_ratio, "nav": nav,
            "total_assets": total_assets, "ytd_return": ytd_return,
            "three_yr_return": three_yr_return, "five_yr_return": five_yr_return,
        }

    except Exception as e:
        return {"error": str(e)}


def fmt(val, suffix="", prefix="", mult=1, decimals=1):
    if val is None:
        return "-"
    return prefix + str(round(val * mult, decimals)) + suffix


def fmt_large(val):
    if val is None:
        return "-"
    if val >= 1e12:
        return str(round(val / 1e12, 2)) + "T"
    if val >= 1e9:
        return str(round(val / 1e9, 2)) + "B"
    if val >= 1e7:
        return str(round(val / 1e7, 2)) + "Cr"
    if val >= 1e5:
        return str(round(val / 1e5, 2)) + "L"
    return str(val)


def chg_arrow(val):
    if val > 0:
        return "+" + str(val) + "%"
    elif val < 0:
        return str(val) + "%"
    return "0%"
