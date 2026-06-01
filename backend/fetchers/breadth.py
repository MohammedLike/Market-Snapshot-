"""
fetchers/breadth.py
Fetches market breadth (Advances/Declines) for Nifty 500.
Since NSE doesn't have a direct easy API for this without session,
we scan the Nifty 500 list via yfinance in bulk.
"""
import yfinance as yf
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Sample of Nifty 500 (Top 100 for speed/breadth proxy)
BREADTH_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "SBI.NS", "HINDUNILVR.NS", "LICI.NS", "ITC.NS",
    "LT.NS", "BAJFINANCE.NS", "KOTAKBANK.NS", "HCLTECH.NS", "AXISBANK.NS",
    "ADANIENT.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "MARUTI.NS",
    "NTPC.NS", "ASIANPAINT.NS", "TATAMOTORS.NS", "POWERGRID.NS", "ADANIPORTS.NS",
    "BAJAJFINSV.NS", "COALINDIA.NS", "JSWSTEEL.NS", "ONGC.NS", "TATASTEEL.NS",
    "M&M.NS", "GRASIM.NS", "ADANIPOWER.NS", "SBILIFE.NS", "INDUSINDBK.NS",
    "HINDALCO.NS", "BAJAJ-AUTO.NS", "NESTLEIND.NS", "BPCL.NS", "CIPLA.NS",
    "BRITANNIA.NS", "EICHERMOT.NS", "TECHM.NS", "WIPRO.NS", "DRREDDY.NS",
    "TATACONSUM.NS", "APOLLOHOSP.NS", "HDFCLIFE.NS", "DIVISLAB.NS", "HEROMOTOCO.NS"
]

def fetch_market_breadth() -> dict:
    """
    Scans a proxy of Nifty 100/500 and returns {adv, dec, ratio}.
    """
    try:
        data = yf.download(
            BREADTH_SYMBOLS,
            period="2d",
            interval="1d",
            group_by="ticker",
            progress=False,
            threads=True,
            auto_adjust=True
        )
        
        adv = 0
        dec = 0
        
        for symbol in BREADTH_SYMBOLS:
            try:
                if symbol not in data.columns.get_level_values(0):
                    continue
                df = data[symbol].dropna()
                if len(df) < 2:
                    continue
                
                change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                if change > 0:
                    adv += 1
                elif change < 0:
                    dec += 1
            except Exception:
                continue
                
        total = adv + dec
        ratio = round(adv / dec, 2) if dec > 0 else (adv if adv > 0 else 1.0)
        
        return {
            "adv": adv,
            "dec": dec,
            "total": total,
            "ratio": ratio,
            "pct": round((adv / total * 100), 1) if total > 0 else 50.0
        }
    except Exception as e:
        logger.error(f"Breadth fetch failed: {e}")
        return {"adv": 25, "dec": 25, "total": 50, "ratio": 1.0, "pct": 50.0}
