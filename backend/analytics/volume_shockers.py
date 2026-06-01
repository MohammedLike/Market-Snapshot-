"""
analytics/volume_shockers.py
Detects stocks with unusual volume (relative volume > 2x 20-day average).
"""
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

# Nifty 500 sample — top liquid F&O names
SCAN_UNIVERSE = [
    ("RELIANCE",    "RELIANCE.NS"),
    ("HDFCBANK",    "HDFCBANK.NS"),
    ("INFY",        "INFY.NS"),
    ("TCS",         "TCS.NS"),
    ("ICICIBANK",   "ICICIBANK.NS"),
    ("AXISBANK",    "AXISBANK.NS"),
    ("SBIN",        "SBIN.NS"),
    ("BAJFINANCE",  "BAJFINANCE.NS"),
    ("WIPRO",       "WIPRO.NS"),
    ("TATAMOTORS",  "TATAMOTORS.NS"),
    ("NUVAMA",      "NUVAMA.NS"),
    ("FINCABLES",   "FINCABLES.NS"),
    ("CRAFTSMAN",   "CRAFTSMAN.NS"),
    ("KALYAN",      "KALYANKJIL.NS"),
    ("NBCC",        "NBCC.NS"),
    ("BRITANNIA",   "BRITANNIA.NS"),
    ("ABB",         "ABB.NS"),
    ("ZOMATO",      "ZOMATO.NS"),
    ("PAYTM",       "PAYTM.NS"),
    ("ADANIENT",    "ADANIENT.NS"),
]

def detect_volume_shockers(max_results: int = 5) -> list[dict]:
    """
    Returns list of { name, tag } for stocks with unusual volume.
    """
    shockers = []

    for name, symbol in SCAN_UNIVERSE:
        if len(shockers) >= max_results:
            break
        try:
            t    = yf.Ticker(symbol)
            hist = t.history(period="25d", interval="1d", auto_adjust=True)
            if len(hist) < 5:
                continue

            today_vol = float(hist["Volume"].iloc[-1])
            avg_vol   = float(hist["Volume"].iloc[:-1].mean())
            if avg_vol == 0:
                continue

            rel_vol = today_vol / avg_vol
            if rel_vol < 1.8:
                continue

            # Classify tag
            price_chg = float(hist["Close"].iloc[-1]) - float(hist["Close"].iloc[-2])
            if price_chg > 0 and rel_vol > 2.5:
                tag = "BREAKOUT"
            elif price_chg < 0 and rel_vol > 2.5:
                tag = "BREAKDOWN"
            elif rel_vol > 3.0:
                tag = "DELIVERY SPIKE"
            else:
                tag = "VOLUME SURGE"

            shockers.append({"name": name, "tag": tag})

        except Exception as e:
            logger.debug(f"Volume scan error for {name}: {e}")

    if not shockers:
        shockers = [
            {"name": "No shockers", "tag": "NORMAL VOL"},
        ]

    return shockers
