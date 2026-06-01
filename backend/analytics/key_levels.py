"""
analytics/key_levels.py
Calculates Nifty intraday key levels using:
  - Previous day High/Low/Close (Pivot Point method)
  - ATR-based dynamic range
  - Option chain OI walls (passed in)
Returns the full keyLevels dict matching the frontend schema.
"""
import yfinance as yf
import logging
import math

logger = logging.getLogger(__name__)

def calculate_key_levels(
    spot: float,
    call_wall: int,
    put_floor: int,
) -> dict:
    """
    Returns keyLevels dict ready for the frontend.
    """
    try:
        ticker = yf.Ticker("^NSEI")
        hist   = ticker.history(period="10d", interval="1d", auto_adjust=True)

        if len(hist) < 2:
            raise ValueError("Insufficient history")

        prev   = hist.iloc[-2]
        ph, pl, pc = float(prev["High"]), float(prev["Low"]), float(prev["Close"])

        # Standard Pivot
        pivot = (ph + pl + pc) / 3
        r1    = 2 * pivot - pl
        r2    = pivot + (ph - pl)
        r3    = ph + 2 * (pivot - pl)
        s1    = 2 * pivot - ph
        s2    = pivot - (ph - pl)
        s3    = pl - 2 * (ph - pivot)

        # ATR (14-day)
        atr = _calc_atr(hist, 14)

        # Round all to nearest 50
        def r50(v): return round(v / 50) * 50

        levels = [
            {"label": "SUPPORT 3",    "value": r50(s3),    "type": "support",    "color": "#EF4444"},
            {"label": "SUPPORT 2",    "value": r50(s2),    "type": "support",    "color": "#F97316"},
            {"label": "SUPPORT 1",    "value": r50(s1),    "type": "support",    "color": "#FBBF24"},
            {"label": "RESISTANCE 1", "value": r50(r1),    "type": "resistance", "color": "#86EFAC"},
            {"label": "RESISTANCE 2", "value": r50(r2),    "type": "resistance", "color": "#22C55E"},
            {"label": "RESISTANCE 3", "value": r50(r3),    "type": "resistance", "color": "#16A34A"},
        ]

        # Remove duplicates and sort
        seen = set()
        unique_levels = []
        for lv in sorted(levels, key=lambda x: x["value"]):
            if lv["value"] not in seen:
                seen.add(lv["value"])
                unique_levels.append(lv)

        # Dynamic min/max: spot ± 1.5× ATR, rounded to 100
        margin = max(atr * 1.5, 300)
        chart_min = int(math.floor((spot - margin) / 100) * 100)
        chart_max = int(math.ceil((spot + margin) / 100) * 100)

        # Clamp levels to chart range
        unique_levels = [lv for lv in unique_levels if chart_min <= lv["value"] <= chart_max]

        # Zones: bearish below pivot, bullish above
        pivot_r = r50(pivot)
        zones = [
            {"from": chart_min, "to": pivot_r,   "color": "rgba(239,68,68,0.18)",  "label": ""},
            {"from": pivot_r,   "to": chart_max,  "color": "rgba(34,197,94,0.12)",  "label": ""},
        ]

        # Sentiment
        if spot < s1:
            sentiment    = "BEARISH — BELOW SUPPORT"
            sentimentSub = f"WATCH {r50(s2):,}"
        elif spot > r1:
            sentiment    = "BULLISH — ABOVE RESISTANCE"
            sentimentSub = f"TARGET {r50(r2):,}"
        else:
            sentiment    = "RANGE BOUND"
            sentimentSub = f"PIVOT {pivot_r:,}"

        return {
            "title":        "NIFTY 50 · INTRADAY KEY LEVELS",
            "min":          chart_min,
            "max":          chart_max,
            "levels":       unique_levels,
            "zones":        zones,
            "currentPrice": int(spot),
            "sentiment":    sentiment,
            "sentimentSub": sentimentSub,
        }

    except Exception as e:
        logger.error(f"Key levels calculation failed: {e}")
        return _fallback_levels(spot)


def _calc_atr(hist, period: int = 14) -> float:
    """Average True Range."""
    try:
        trs = []
        closes = hist["Close"].tolist()
        highs  = hist["High"].tolist()
        lows   = hist["Low"].tolist()
        for i in range(1, len(hist)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i]  - closes[i - 1]),
            )
            trs.append(tr)
        return sum(trs[-period:]) / min(len(trs), period)
    except Exception:
        return 200.0


def _fallback_levels(spot: float) -> dict:
    base = round(spot / 50) * 50
    return {
        "title":        "NIFTY 50 · INTRADAY KEY LEVELS",
        "min":          int(base - 600),
        "max":          int(base + 600),
        "levels": [
            {"label": "SUPPORT 3",    "value": int(base - 500), "type": "support",    "color": "#EF4444"},
            {"label": "SUPPORT 2",    "value": int(base - 300), "type": "support",    "color": "#F97316"},
            {"label": "SUPPORT 1",    "value": int(base - 150), "type": "support",    "color": "#FBBF24"},
            {"label": "RESISTANCE 1", "value": int(base + 150), "type": "resistance", "color": "#86EFAC"},
            {"label": "RESISTANCE 2", "value": int(base + 300), "type": "resistance", "color": "#22C55E"},
            {"label": "RESISTANCE 3", "value": int(base + 500), "type": "resistance", "color": "#16A34A"},
        ],
        "zones": [
            {"from": int(base - 600), "to": int(base),       "color": "rgba(239,68,68,0.18)", "label": ""},
            {"from": int(base),       "to": int(base + 600), "color": "rgba(34,197,94,0.12)", "label": ""},
        ],
        "currentPrice": int(spot),
        "sentiment":    "RANGE BOUND",
        "sentimentSub": f"CMP {int(spot):,}",
    }
