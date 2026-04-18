"""
Market Sentiment Agent - No LLMChain dependency
"""

from engines.mamba_engine import get_balanced_llm
from config.settings import NEWS_API_KEY

try:
    from newsapi import NewsApiClient
    HAS_NEWSAPI = True
except ImportError:
    HAS_NEWSAPI = False


class SentimentAgent:
    """Market news and sentiment analysis"""

    def __init__(self):
        if HAS_NEWSAPI and NEWS_API_KEY:
            self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        else:
            self.newsapi = None
        self.llm = get_balanced_llm()

    def get_stock_news(self, query):
        """Fetch recent news"""
        if not self.newsapi:
            return [{"title": "NewsAPI not configured"}]

        try:
            articles = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=10
            )

            news = []
            for a in articles.get('articles', []):
                news.append({
                    "title": a.get('title', ''),
                    "description": a.get('description', ''),
                    "source": a.get('source', {}).get('name', ''),
                })
            return news if news else [{"title": "No news found"}]

        except Exception as e:
            return [{"title": "Error: " + str(e)}]

    def analyze_sentiment(self, ticker, company_name):
        """Analyze sentiment for a stock"""
        news = self.get_stock_news(company_name)

        prompt = """You are a market sentiment analyst.

Company: """ + company_name + """ (""" + ticker + """)

Recent News:
""" + str(news) + """

## Analyze:

### 1. OVERALL SENTIMENT
Bullish / Bearish / Neutral (with confidence %)

### 2. KEY THEMES

### 3. CATALYSTS
- Positive
- Negative

### 4. SENTIMENT TREND
Improving or deteriorating?

### 5. IMPACT ASSESSMENT
- Short-term price impact
- Medium-term price impact

Disclaimer: Not financial advice.
"""
        return self.llm(prompt)

    def market_overview(self):
        """Overall market sentiment"""
        news = self.get_stock_news("stock market India economy")

        prompt = """You are a market strategist.

Market News:
""" + str(news) + """

## Provide:

### 1. MARKET MOOD: Bullish / Bearish / Cautious

### 2. SECTOR OUTLOOK
- Strong sectors
- Weak sectors

### 3. KEY EVENTS AHEAD

### 4. STRATEGY
- For aggressive investors
- For conservative investors
- For SIP investors

Disclaimer: Educational only.
"""
        return self.llm(prompt)


if __name__ == "__main__":
    agent = SentimentAgent()
    print("Sentiment Agent loaded OK")