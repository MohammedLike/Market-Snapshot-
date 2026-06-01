"""
analytics/market_mood.py
Heuristic-based AI summary generator for the market snapshot.
Simulates a professional analyst's summary of the data.
"""
import logging

logger = logging.getLogger(__name__)

def generate_ai_mood(data: dict) -> dict:
    """
    Analyzes the full snapshot payload and generates a 2-sentence summary.
    """
    try:
        nifty_pct = data.get("ticker", [{}])[0].get("value", "0").split("(")[-1].replace("%)", "")
        nifty_pct = float(nifty_pct) if nifty_pct else 0.0
        
        fii_ratio = data.get("fiiRatio", {}).get("ratio", 0.5)
        breadth_pct = data.get("advances", {}).get("pct", 50)
        vix = data.get("niftyOutlook", {}).get("levels", [{}])[-1].get("value", "15")
        vix = float(vix) if vix else 15.0
        
        # ── Intelligence Logic ──
        mood_tags = []
        
        # Trend
        if nifty_pct > 0.5: trend = "bullish momentum"
        elif nifty_pct < -0.5: trend = "selling pressure"
        else: trend = "sideways consolidation"
        
        # Institutional
        if fii_ratio < 0.45: inst = "FIIs remain cautious with heavy shorts"
        elif fii_ratio > 0.55: inst = "Strong institutional accumulation detected"
        else: inst = "Institutions are in a wait-and-watch mode"
        
        # Risk
        if vix > 18: risk = "high volatility ahead"
        else: risk = "low volatility environment"
        
        # ── Summary Construction ──
        summary = f"The market is currently seeing {trend}, while {inst}. "
        summary += f"With {risk} and breadth at {breadth_pct}%, "
        
        if breadth_pct > 60 and nifty_pct > 0:
            summary += "the current rally looks healthy and broad-based."
            headline = "HEALTHY RALLY"
            color = "var(--brand-green)"
        elif breadth_pct < 40 and nifty_pct < 0:
            summary += "caution is advised as the decline is widespread."
            headline = "WEAK BREADTH"
            color = "var(--brand-red)"
        else:
            summary += "traders should focus on stock-specific moves near key levels."
            headline = "MIXED MOOD"
            color = "#F59E0B"

        return {
            "headline": headline,
            "summary": summary,
            "color": color
        }
    except Exception as e:
        logger.error(f"AI Mood generation failed: {e}")
        return {
            "headline": "NEUTRAL",
            "summary": "Market data is mixed. Maintain discipline and watch key support levels.",
            "color": "#64748B"
        }
