"""
analytics/sentiment.py
Builds a composite market sentiment score from:
  - Price action (Nifty % change)
  - Breadth (advances/declines)
  - FII/DII flows
  - VIX level
  - Global markets
Returns: { label, score, confidence, riskTags }
"""
import logging

logger = logging.getLogger(__name__)

def calculate_sentiment(
    nifty_pct:    float,
    adv:          int,
    dec:          int,
    fii_today:    float,
    vix:          float,
    global_pct:   float,   # average of Dow/Nasdaq/S&P change
) -> dict:
    """
    Returns sentiment dict.
    score: -100 (max bearish) to +100 (max bullish)
    """
    score = 0.0

    # 1. Price action (weight: 30)
    score += max(-30, min(30, nifty_pct * 10))

    # 2. Breadth (weight: 20)
    total = adv + dec
    if total > 0:
        breadth_ratio = (adv - dec) / total   # -1 to +1
        score += breadth_ratio * 20

    # 3. FII flow (weight: 25)
    # Normalise: ±5000 cr = ±25 points
    score += max(-25, min(25, fii_today / 200))

    # 4. VIX (weight: 15) — high VIX = bearish
    if vix > 0:
        if vix > 20:
            score -= 15
        elif vix > 15:
            score -= 8
        elif vix < 12:
            score += 10
        else:
            score += 5

    # 5. Global markets (weight: 10)
    score += max(-10, min(10, global_pct * 3))

    score = round(max(-100, min(100, score)), 1)

    # Label
    if score >= 40:
        label = "BULLISH"
        color = "#16A34A"
    elif score >= 10:
        label = "MILDLY BULLISH"
        color = "#22C55E"
    elif score >= -10:
        label = "NEUTRAL"
        color = "#F59E0B"
    elif score >= -40:
        label = "MILDLY BEARISH"
        color = "#F97316"
    else:
        label = "BEARISH"
        color = "#DC2626"

    confidence = round(abs(score), 1)

    # Risk tags
    tags = []
    if nifty_pct < -1:
        tags.append("BEARS IN CONTROL")
    elif nifty_pct > 1:
        tags.append("BULLS IN CONTROL")

    if vix > 18:
        tags.append("HIGH VOLATILITY")
    if fii_today < -2000:
        tags.append(f"FII SELLING: ₹{abs(fii_today):,.0f}cr")
    elif fii_today > 2000:
        tags.append(f"FII BUYING: ₹{fii_today:,.0f}cr")

    if global_pct < -0.5:
        tags.append("GLOBAL WEAKNESS")
    elif global_pct > 0.5:
        tags.append("GLOBAL STRENGTH")

    if not tags:
        tags = ["RANGE BOUND", "WATCH KEY LEVELS"]

    return {
        "label":      label,
        "score":      score,
        "confidence": confidence,
        "color":      color,
        "riskTags":   tags[:3],   # max 3 tags for header
    }
