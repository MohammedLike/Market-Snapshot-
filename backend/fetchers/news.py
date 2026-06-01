"""
fetchers/news.py
Fetches market-moving news from yfinance (Yahoo Finance RSS).
Returns top N news items formatted for the NewsBoard component.
"""
import yfinance as yf
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Symbols to pull news from
NEWS_SYMBOLS = ["^NSEI", "^NSEBANK", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"]

def fetch_news(max_items: int = 6) -> list[dict]:
    """
    Returns list of { company, headline } dicts.
    """
    seen_titles = set()
    news_items  = []

    for symbol in NEWS_SYMBOLS:
        if len(news_items) >= max_items:
            break
        try:
            ticker = yf.Ticker(symbol)
            raw_news = ticker.news or []
            for item in raw_news:
                # Handle both new nested structure and old flat structure
                content = item.get("content", {})
                title = content.get("title") if content else item.get("title")
                
                if not title:
                    continue
                
                title = title.strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                # Derive a short company label from the symbol
                company = _symbol_to_label(symbol)

                # Truncate headline to 45 chars
                headline = title if len(title) <= 45 else title[:42] + "…"

                news_items.append({
                    "company":  company,
                    "headline": headline,
                })

                if len(news_items) >= max_items:
                    break
        except Exception as e:
            logger.error(f"News fetch error for {symbol}: {e}")

    return news_items if news_items else _fallback_news()


def _symbol_to_label(symbol: str) -> str:
    mapping = {
        "^NSEI":       "NSE",
        "^NSEBANK":    "Bank Nifty",
        "RELIANCE.NS": "Reliance",
        "HDFCBANK.NS": "HDFC Bank",
        "INFY.NS":     "Infosys",
    }
    return mapping.get(symbol, symbol.replace(".NS", "").replace("^", ""))


def _fallback_news() -> list[dict]:
    return [
        {"company": "NSE",      "headline": "Market data unavailable"},
        {"company": "BSE",      "headline": "Check NSE website for updates"},
    ]
