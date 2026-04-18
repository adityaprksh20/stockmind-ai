"""
Centralized Configuration for StockMind + Jyotish AI
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# API KEYS
# ============================================
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")

# ============================================
# MODEL SETTINGS
# ============================================
# Groq model ID
GROQ_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

# Together AI model ID  
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

# Fallback model (smaller, faster)
GROQ_FALLBACK_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

MAMBA_MODEL = GROQ_MODEL  # Keep for backward compatibility
MAMBA_MAX_TOKENS = 4096
MAMBA_TEMP_FACTUAL = 0.1
MAMBA_TEMP_BALANCED = 0.3
MAMBA_TEMP_CREATIVE = 0.5

# ============================================
# STOCK MARKET SETTINGS
# ============================================

# Indian Market (NSE)
NIFTY50_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS",
    "ITC.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS",
    "BAJFINANCE.NS", "WIPRO.NS", "HCLTECH.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "POWERGRID.NS", "NTPC.NS", "M&M.NS", "TECHM.NS",
    "INDUSINDBK.NS", "JSWSTEEL.NS", "ADANIENT.NS"
]

# US Market
US_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "PG", "UNH", "HD", "MA",
    "DIS", "PYPL", "NFLX", "ADBE", "CRM"
]

# Popular Mutual Funds (India)
MUTUAL_FUNDS = {
    "Large Cap": [
        "SBI Bluechip Fund",
        "Mirae Asset Large Cap Fund",
        "Axis Bluechip Fund"
    ],
    "Mid Cap": [
        "HDFC Mid-Cap Opportunities Fund",
        "Kotak Emerging Equity Fund",
        "Axis Midcap Fund"
    ],
    "Small Cap": [
        "SBI Small Cap Fund",
        "Nippon India Small Cap Fund",
        "Axis Small Cap Fund"
    ],
    "Index": [
        "UTI Nifty 50 Index Fund",
        "HDFC Index Fund Nifty 50",
        "Nippon India Nifty 50 BeES"
    ],
    "ELSS (Tax Saving)": [
        "Axis Long Term Equity Fund",
        "Mirae Asset Tax Saver Fund",
        "SBI Long Term Equity Fund"
    ]
}

# ============================================
# JYOTISH SETTINGS
# ============================================
AYANAMSHA_LAHIRI_2024 = 24.17
DEFAULT_LOCATION = {
    "city": "Delhi",
    "country": "IN",
    "lat": 28.6139,
    "lon": 77.2090
}

# ============================================
# APP SETTINGS
# ============================================
APP_TITLE = "🪐 StockMind + JyotishMarket AI"
APP_ICON = "🪐"
MAX_FREE_QUERIES = 5  # Per day for free tier

# Disclaimers
FINANCIAL_DISCLAIMER = """
⚠️ **Financial Disclaimer:** This is AI-generated analysis for 
educational purposes only. This is NOT financial advice. Always 
consult a SEBI-registered investment advisor before making any 
investment decisions. Past performance does not guarantee future 
results.
"""

JYOTISH_DISCLAIMER = """
🪐 **Jyotish Disclaimer:** Astrological predictions are speculative 
in nature and based on Vedic Astrology principles. They should NOT 
be the sole basis for any financial decisions. These predictions are 
for entertainment and educational purposes only.
"""

COMBINED_DISCLAIMER = FINANCIAL_DISCLAIMER + "\n" + JYOTISH_DISCLAIMER


# Validation
def validate_config():
    """Check if all required API keys are set"""
    issues = []
    
    if not TOGETHER_API_KEY:
        issues.append("❌ TOGETHER_API_KEY not set in .env")
    else:
        print("✅ Together AI API key found")
    
    if not NEWS_API_KEY:
        issues.append("⚠️ NEWS_API_KEY not set (sentiment agent won't work)")
    else:
        print("✅ News API key found")
    
    if not LANGCHAIN_API_KEY:
        issues.append("⚠️ LANGCHAIN_API_KEY not set (monitoring disabled)")
    else:
        print("✅ LangSmith API key found")
    
    if issues:
        print("\n".join(issues))
        print("\n💡 Add missing keys to your .env file")
    else:
        print("✅ All API keys configured!")
    
    return len([i for i in issues if i.startswith("❌")]) == 0


if __name__ == "__main__":
    validate_config()
