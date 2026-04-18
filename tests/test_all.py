"""
Quick Verification Tests
Run from project root: python -m tests.test_all
"""

import sys
import os

# Add project root to path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_imports():
    """Test all imports work"""
    print("=" * 60)
    print("TEST 1: Checking Imports")
    print("=" * 60)

    tests = []

    # Config
    try:
        from config.settings import APP_TITLE, NIFTY50_TICKERS
        tests.append(("config.settings", True, ""))
    except Exception as e:
        tests.append(("config.settings", False, str(e)))

    # Engines
    try:
        from engines.mamba_engine import Mamba2LLM, get_balanced_llm
        tests.append(("engines.mamba_engine", True, ""))
    except Exception as e:
        tests.append(("engines.mamba_engine", False, str(e)))

    try:
        from engines.ephemeris_engine import EphemerisEngine
        tests.append(("engines.ephemeris_engine", True, ""))
    except Exception as e:
        tests.append(("engines.ephemeris_engine", False, str(e)))

    # Agents
    try:
        from agents.stock_data_agent import StockDataAgent
        tests.append(("agents.stock_data_agent", True, ""))
    except Exception as e:
        tests.append(("agents.stock_data_agent", False, str(e)))

    try:
        from agents.analysis_chain import StockAnalysisChain
        tests.append(("agents.analysis_chain", True, ""))
    except Exception as e:
        tests.append(("agents.analysis_chain", False, str(e)))

    try:
        from agents.sentiment_agent import SentimentAgent
        tests.append(("agents.sentiment_agent", True, ""))
    except Exception as e:
        tests.append(("agents.sentiment_agent", False, str(e)))

    try:
        from agents.jyotish_agent import JyotishAgent
        tests.append(("agents.jyotish_agent", True, ""))
    except Exception as e:
        tests.append(("agents.jyotish_agent", False, str(e)))

    try:
        from agents.unified_advisor import UnifiedAdvisor
        tests.append(("agents.unified_advisor", True, ""))
    except Exception as e:
        tests.append(("agents.unified_advisor", False, str(e)))

    # Print results
    for module, passed, error in tests:
        if passed:
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module}: {error}")

    failed = sum(1 for _, p, _ in tests if not p)
    print(f"\n  Results: {len(tests) - failed}/{len(tests)} passed")
    return failed == 0


def test_libraries():
    """Test required libraries"""
    print("\n" + "=" * 60)
    print("TEST 2: Checking Libraries")
    print("=" * 60)

    required = [
        ("langchain", "LangChain"),
        ("together", "Together AI"),
        ("yfinance", "Yahoo Finance"),
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly"),
        ("dotenv", "python-dotenv"),
    ]

    optional = [
        ("kerykeion", "Kerykeion (Astrology)"),
        ("newsapi", "NewsAPI"),
        ("chromadb", "ChromaDB"),
    ]

    all_good = True

    print("\n  Required:")
    for lib, name in required:
        try:
            __import__(lib)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - pip install {lib}")
            all_good = False

    print("\n  Optional:")
    for lib, name in optional:
        try:
            __import__(lib)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️  {name} - pip install {lib}")

    return all_good


def test_env():
    """Test environment variables"""
    print("\n" + "=" * 60)
    print("TEST 3: Checking Environment")
    print("=" * 60)

    from config.settings import validate_config
    return validate_config()


def test_ephemeris():
    """Test planetary calculations"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Ephemeris")
    print("=" * 60)

    try:
        from engines.ephemeris_engine import EphemerisEngine
        engine = EphemerisEngine()

        positions = engine.get_planetary_positions()
        print(f"\n  Planets found: {len(positions)}")

        for planet, data in positions.items():
            retro = " ℞" if data.get("retrograde") else ""
            print(
                f"    {planet:10s}: {data['sign']:13s} "
                f"{data['degree']:6.2f}°{retro}"
            )

        report = engine.get_market_report()
        print(f"\n  Market Mood: {report['market_mood']}")
        print("  ✅ Ephemeris working!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stock_data():
    """Test stock data fetching"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Stock Data")
    print("=" * 60)

    try:
        from agents.stock_data_agent import StockDataAgent
        agent = StockDataAgent()

        print("\n  Fetching RELIANCE.NS...")
        info = agent.get_stock_info("RELIANCE.NS")
        print(f"    Name: {info.get('name', 'N/A')}")
        print(f"    Price: {info.get('current_price', 'N/A')}")
        print(f"    PE: {info.get('pe_ratio', 'N/A')}")

        print("  ✅ Stock Data working!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def test_mamba():
    """Test Mamba2 API"""
    print("\n" + "=" * 60)
    print("TEST 6: Testing Mamba2")
    print("=" * 60)

    try:
        from config.settings import TOGETHER_API_KEY

        if not TOGETHER_API_KEY:
            print("  ⚠️  API key not set. Skipping.")
            return True

        from engines.mamba_engine import get_balanced_llm
        llm = get_balanced_llm()

        print("  Sending test query...")
        result = llm("What is 2+2? Answer in one word:")
        print(f"  Response: {result.strip()[:100]}")
        print("  ✅ Mamba2 working!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def run_all():
    """Run all tests"""
    print("\n" + "🔬 " * 20)
    print("  STOCKMIND + JYOTISH AI - TEST SUITE")
    print("🔬 " * 20)

    results = {
        "imports": test_imports(),
        "libraries": test_libraries(),
        "env": test_env(),
        "ephemeris": test_ephemeris(),
        "stock_data": test_stock_data(),
        "mamba": test_mamba(),
    }

    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} : {name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed}/{total} passed")

    if passed == total:
        print("\n  🎉 ALL PASSED! Run: streamlit run app.py")
    else:
        print("\n  ⚠️  Fix failures above first.")

    return passed == total


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)