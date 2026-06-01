"""
fetchers/market_data.py
Fetches live prices for all ticker symbols via yfinance.
Returns a normalised dict keyed by display label.
"""
import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ── Symbol map ────────────────────────────────────────────────
SYMBOLS = {
    "NIFTY 50":      "^NSEI",
    "BANK NIFTY":    "^NSEBANK",
    "FIN NIFTY":     "NIFTY_FIN_SERVICE.NS",
    "MIDCAP 100":    "^CNXMID",
    "SMALLCAP 100":  "^CNXSC",
    "BRENT":         "BZ=F",
    "USDINR":        "INR=X",
    "DXY":           "DX-Y.NYB",
    "DOW":           "^DJI",
    "NASDAQ":        "^IXIC",
    "S&P 500":       "^GSPC",
    "FTSE":          "^FTSE",
    "DAX":           "^GDAXI",
    "NIKKEI":        "^N225",
    "HANG SENG":     "^HSI",
    "SHANGHAI":      "000001.SS",
    "INDIA VIX":     "^INDIAVIX",
}

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        return default

def fetch_all() -> dict:
    """
    Returns dict[label] = {
        val, prev_close, change, change_pct, high, low, open, volume
    }
    """
    results = {}
    tickers = list(SYMBOLS.values())

    try:
        data = yf.download(
            tickers,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        logger.error(f"Bulk download failed: {e}")
        data = None

    for label, symbol in SYMBOLS.items():
        try:
            if data is not None and symbol in data.columns.get_level_values(0):
                df = data[symbol].dropna()
            else:
                # Fallback: individual fetch
                t = yf.Ticker(symbol)
                df = t.history(period="5d", interval="1d", auto_adjust=True)

            if df.empty:
                logger.warning(f"No data for {label} ({symbol})")
                continue

            close      = _safe_float(df["Close"].iloc[-1])
            prev_close = _safe_float(df["Close"].iloc[-2]) if len(df) >= 2 else close
            change     = close - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0.0

            results[label] = {
                "val":        round(close, 2),
                "prev_close": round(prev_close, 2),
                "change":     round(change, 2),
                "change_pct": round(change_pct, 2),
                "high":       round(_safe_float(df["High"].iloc[-1]), 2),
                "low":        round(_safe_float(df["Low"].iloc[-1]), 2),
                "open":       round(_safe_float(df["Open"].iloc[-1]), 2),
                "volume":     int(_safe_float(df["Volume"].iloc[-1])),
            }
        except Exception as e:
            logger.error(f"Error processing {label}: {e}")

    return results


def fetch_sparkline(symbol: str, days: int = 10) -> list[float]:
    """Returns a list of closing prices for the sparkline chart."""
    try:
        t = yf.Ticker(symbol)
        df = t.history(period=f"{days}d", interval="1d", auto_adjust=True)
        return [round(float(v), 2) for v in df["Close"].dropna().tolist()]
    except Exception as e:
        logger.error(f"Sparkline error for {symbol}: {e}")
        return []
