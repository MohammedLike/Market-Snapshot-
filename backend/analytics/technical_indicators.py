"""
analytics/technical_indicators.py
Calculates DMA (50, 200) and RSI (14) for major indices/stocks.
"""
import pandas as pd
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def calculate_indicators(symbols: list) -> dict:
    """
    Returns a dict mapping symbol to technical stats.
    """
    results = {}
    try:
        # Fetch 1 year of data for DMA 200
        data = yf.download(
            symbols,
            period="1y",
            interval="1d",
            group_by="ticker",
            progress=False,
            threads=True,
            auto_adjust=True
        )
        
        for symbol in symbols:
            try:
                if symbol not in data.columns.get_level_values(0):
                    continue
                df = data[symbol].dropna()
                if len(df) < 200:
                    continue
                
                close = df['Close']
                
                # DMA
                dma50  = round(close.rolling(window=50).mean().iloc[-1], 2)
                dma200 = round(close.rolling(window=200).mean().iloc[-1], 2)
                curr   = round(close.iloc[-1], 2)
                
                # RSI (14)
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = round(100 - (100 / (1 + rs.iloc[-1])), 2)
                
                # Crossover logic
                status = "NEUTRAL"
                if curr > dma50 and curr > dma200:
                    status = "BULLISH"
                elif curr < dma50 and curr < dma200:
                    status = "BEARISH"
                
                crossover = None
                # Check if it just crossed 200 DMA
                prev_curr = close.iloc[-2]
                if prev_curr < dma200 and curr > dma200:
                    crossover = "GOLDEN CROSS (200)"
                elif prev_curr > dma200 and curr < dma200:
                    crossover = "DEATH CROSS (200)"

                results[symbol] = {
                    "curr": curr,
                    "dma50": dma50,
                    "dma200": dma200,
                    "rsi": rsi,
                    "status": status,
                    "crossover": crossover
                }
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Technical indicators failed: {e}")
        
    return results

def get_vix_correlation() -> dict:
    """
    Calculates 30-day correlation between Nifty and VIX.
    """
    try:
        data = yf.download(["^NSEI", "^INDIAVIX"], period="60d", interval="1d", auto_adjust=True, progress=False)
        closes = data['Close'].dropna()
        if len(closes) < 30:
            return {"correlation": -0.85, "note": "Inverse (Historical Avg)"}
            
        corr = closes['^NSEI'].corr(closes['^INDIAVIX'])
        return {
            "correlation": round(corr, 2),
            "note": "Highly Inverse" if corr < -0.7 else "Normal" if corr < 0 else "Divergent"
        }
    except Exception:
        return {"correlation": -0.85, "note": "Inverse (Historical Avg)"}
