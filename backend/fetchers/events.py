"""
fetchers/events.py
Fetches upcoming economic events and calculates global pre-market correlations.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_economic_calendar() -> list:
    """
    Returns upcoming high-impact economic events.
    """
    # For this prototype, we return high-probability recurring macro events
    # In production, this would fetch from an API like Investing.com or TradingEconomics
    today = datetime.now()
    events = [
        {"date": (today + timedelta(days=2)).strftime("%d %b"), "event": "RBI Monetary Policy", "impact": "HIGH"},
        {"date": (today + timedelta(days=5)).strftime("%d %b"), "event": "US Fed Meeting", "impact": "HIGH"},
        {"date": (today + timedelta(days=12)).strftime("%d %b"), "event": "India CPI Inflation", "impact": "MEDIUM"},
        {"date": (today + timedelta(days=15)).strftime("%d %b"), "event": "US Non-Farm Payrolls", "impact": "HIGH"},
    ]
    return events

def calculate_global_alignment(market_data: dict) -> dict:
    """
    Analyzes how aligned global indices are (Gift Nifty, Nikkei, Dow Futures).
    Returns a 'Confidence Score' for the opening direction.
    """
    try:
        dow = market_data.get("DOW", {}).get("change_pct", 0)
        nasdaq = market_data.get("NASDAQ", {}).get("change_pct", 0)
        ftse = market_data.get("FTSE", {}).get("change_pct", 0)
        
        # Calculate alignment
        signals = [dow > 0, nasdaq > 0, ftse > 0]
        bullish_count = sum(signals)
        
        score = 0
        if bullish_count == 3:
            score = 85
            label = "STRONG BULLISH ALIGNMENT"
        elif bullish_count == 0:
            score = 85
            label = "STRONG BEARISH ALIGNMENT"
        elif bullish_count == 2:
            score = 60
            label = "MODERATE BULLISH BIAS"
        else:
            score = 60
            label = "MODERATE BEARISH BIAS"
            
        return {
            "score": score,
            "label": label,
            "alignment": f"{bullish_count}/3 Indices Positive"
        }
    except Exception:
        return {"score": 50, "label": "MIXED GLOBAL CUES", "alignment": "N/A"}
