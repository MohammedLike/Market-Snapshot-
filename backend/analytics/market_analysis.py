"""
analytics/market_analysis.py
Generates rule-based market analysis text (no AI API required).
Produces professional research-note style commentary for:
  - Global Cues
  - Nifty Outlook
  - Technical Note
"""
from datetime import datetime

def generate_global_cues(market_data: dict) -> dict:
    """
    Generates global cues commentary from live global market data.
    """
    dow    = market_data.get("DOW",     {})
    nasdaq = market_data.get("NASDAQ",  {})
    sp500  = market_data.get("S&P 500", {})
    ftse   = market_data.get("FTSE",    {})
    dax    = market_data.get("DAX",     {})
    nikkei = market_data.get("NIKKEI",  {})
    brent  = market_data.get("BRENT",   {})

    dow_pct    = dow.get("change_pct",    0)
    nasdaq_pct = nasdaq.get("change_pct", 0)
    brent_pct  = brent.get("change_pct",  0)
    brent_val  = brent.get("val",         0)

    # Determine headline theme
    if brent_pct > 2:
        headline = f"Oil Surges — Brent at ${brent_val:.2f}"
        tags     = ["ENERGY INFLATION", "COMMODITY RALLY"]
    elif brent_pct < -2:
        headline = f"Oil Drops — Brent Falls to ${brent_val:.2f}"
        tags     = ["ENERGY DEFLATION", "DEMAND CONCERNS"]
    elif nasdaq_pct > 1.5:
        headline = "Tech Rally Lifts Global Sentiment"
        tags     = ["RISK ON", "TECH STRENGTH"]
    elif nasdaq_pct < -1.5:
        headline = "Tech Selloff Weighs on Global Markets"
        tags     = ["RISK OFF", "TECH WEAKNESS"]
    elif dow_pct > 0.5:
        headline = "Wall Street Closes Higher"
        tags     = ["POSITIVE GLOBAL CUES", "RISK ON"]
    elif dow_pct < -0.5:
        headline = "Wall Street Closes in Red"
        tags     = ["NEGATIVE GLOBAL CUES", "RISK OFF"]
    else:
        headline = "Mixed Global Signals"
        tags     = ["RANGE BOUND", "WATCH LEVELS"]

    # Body text
    parts = []
    if dow_pct != 0:
        parts.append(f"Dow Jones {'gained' if dow_pct > 0 else 'lost'} {abs(dow_pct):.2f}%")
    if nasdaq_pct != 0:
        parts.append(f"Nasdaq {'rose' if nasdaq_pct > 0 else 'fell'} {abs(nasdaq_pct):.2f}%")
    if brent_val > 0:
        parts.append(f"Brent Crude at ${brent_val:.2f} ({brent_pct:+.2f}%)")
    if nikkei.get("change_pct"):
        parts.append(f"Nikkei {nikkei['change_pct']:+.2f}%")

    body = ". ".join(parts) + "." if parts else "Global markets data unavailable."
    body += " Domestic markets will take cues from overnight moves and pre-open Gift Nifty."

    return {"headline": headline, "body": body, "tags": tags}


def generate_nifty_outlook(
    nifty_data:  dict,
    key_levels:  dict,
    adv:         int,
    dec:         int,
    vix:         float,
) -> dict:
    """
    Generates Nifty closing analysis and outlook levels.
    """
    close     = nifty_data.get("val",        0)
    change    = nifty_data.get("change",     0)
    change_pct= nifty_data.get("change_pct", 0)
    high      = nifty_data.get("high",       0)
    low       = nifty_data.get("low",        0)

    # Title
    if change_pct < -1.5:
        title = "Sharp Selloff — Bears Dominate"
    elif change_pct < -0.5:
        title = "Weak Close — Caution Advised"
    elif change_pct > 1.5:
        title = "Strong Rally — Bulls in Control"
    elif change_pct > 0.5:
        title = "Positive Close — Momentum Intact"
    else:
        title = "Rangebound Session — Indecision"

    # Body
    breadth_str = f"{adv} advances vs {dec} declines"
    vix_str     = f"India VIX at {vix:.2f}" if vix > 0 else ""
    body = (
        f"Nifty 50 closed at {close:,.2f}, {'down' if change < 0 else 'up'} "
        f"{abs(change):.2f} points ({change_pct:+.2f}%). "
        f"Day range: {low:,.2f} – {high:,.2f}. "
        f"Market breadth: {breadth_str}. "
    )
    if vix_str:
        body += f"{vix_str}. "

    # Outlook levels from key_levels
    levels_raw = key_levels.get("levels", [])
    supports    = [lv for lv in levels_raw if "SUPPORT" in lv["label"]]
    resistances = [lv for lv in levels_raw if "RESISTANCE" in lv["label"]]

    outlook_levels = []
    if supports:
        s1 = supports[-1]  # closest support
        outlook_levels.append({
            "label": "IMMEDIATE SUPPORT",
            "value": f"{s1['value']:,}",
            "sub":   "Watch closely",
            "color": "#EF4444",
        })
    if len(supports) >= 2:
        s2 = supports[-2]
        outlook_levels.append({
            "label": "CRUCIAL FLOOR",
            "value": f"{s2['value']:,}",
            "sub":   "Heavy pressure below",
            "color": "#F97316",
        })
    if resistances:
        r1 = resistances[0]
        outlook_levels.append({
            "label": "RESISTANCE",
            "value": f"{r1['value']:,}",
            "sub":   "Breakout needed",
            "color": "#22C55E",
        })
    if vix > 0:
        outlook_levels.append({
            "label": "INDIA VIX",
            "value": f"{vix:.2f}",
            "sub":   "Up" if vix > 15 else "Stable",
            "color": "#EF4444" if vix > 18 else "#F59E0B",
        })

    # Pad to 4 cells
    while len(outlook_levels) < 4:
        outlook_levels.append({
            "label": "PIVOT",
            "value": f"{key_levels.get('currentPrice', int(close)):,}",
            "sub":   "Key reference",
            "color": "#64748B",
        })

    return {
        "title":  title,
        "body":   body,
        "levels": outlook_levels[:4],
    }


def generate_technical_note(
    nifty_data:  dict,
    key_levels:  dict,
    fii_today:   float,
    sentiment:   str,
) -> str:
    """
    Returns a short technical note paragraph.
    """
    close      = nifty_data.get("val",        0)
    change_pct = nifty_data.get("change_pct", 0)
    levels     = key_levels.get("levels",     [])
    supports   = [lv for lv in levels if "SUPPORT" in lv["label"]]
    resistances= [lv for lv in levels if "RESISTANCE" in lv["label"]]

    note = f"Nifty 50 at {close:,.2f} ({change_pct:+.2f}%). "

    if supports:
        note += f"Immediate support at {supports[-1]['value']:,}. "
    if resistances:
        note += f"Resistance at {resistances[0]['value']:,}. "

    if fii_today < -2000:
        note += f"FII sold ₹{abs(fii_today):,.0f} cr — institutional pressure remains. "
    elif fii_today > 2000:
        note += f"FII bought ₹{fii_today:,.0f} cr — institutional support visible. "

    note += f"Overall bias: {sentiment}."
    return note
