"""
snapshot_builder.py
Orchestrates all fetchers and analytics into a single snapshot dict
that exactly matches the frontend's marketSnapshot.json schema.
"""
import logging
from datetime import datetime
import pytz

from fetchers.market_data    import fetch_all, fetch_sparkline
from fetchers.options_oi     import fetch_options_oi
from fetchers.fii_dii        import fetch_fii_dii
from fetchers.news           import fetch_news
from analytics.key_levels    import calculate_key_levels
from analytics.smart_money   import detect_smart_money
from analytics.sentiment     import calculate_sentiment
from analytics.volume_shockers import detect_volume_shockers
from analytics.market_analysis import (
    generate_global_cues,
    generate_nifty_outlook,
    generate_technical_note,
)

logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")


def build_snapshot() -> dict:
    """
    Full pipeline: fetch → calculate → assemble → return dict.
    Never raises — always returns a valid dict (may contain stale/fallback data).
    """
    logger.info("Building snapshot...")
    now_ist = datetime.now(IST)

    # ── 1. Fetch all market prices ────────────────────────────
    market = fetch_all()
    logger.info(f"Market data fetched: {len(market)} symbols")

    nifty  = market.get("NIFTY 50",   {})
    bnifty = market.get("BANK NIFTY", {})
    brent  = market.get("BRENT",      {})
    vix    = market.get("INDIA VIX",  {})

    nifty_spot     = nifty.get("val",        24000.0)
    nifty_pct      = nifty.get("change_pct", 0.0)
    vix_val        = vix.get("val",          14.0)

    # ── 2. Options OI ─────────────────────────────────────────
    oi_data = fetch_options_oi(nifty_spot)
    logger.info("OI data fetched")

    # ── 3. FII/DII ────────────────────────────────────────────
    fii_dii = fetch_fii_dii()
    fii_today = fii_dii["fii"]["today"]
    logger.info("FII/DII data fetched")

    # ── 4. Key Levels ─────────────────────────────────────────
    key_levels = calculate_key_levels(
        spot=nifty_spot,
        call_wall=oi_data["callWall"],
        put_floor=oi_data["putFloor"],
    )
    logger.info("Key levels calculated")

    # ── 5. Sentiment ──────────────────────────────────────────
    global_avg_pct = _avg_pct(market, ["DOW", "NASDAQ", "S&P 500"])
    adv = 1200   # placeholder — NSE breadth not in yfinance
    dec = 1100
    sentiment = calculate_sentiment(
        nifty_pct=nifty_pct,
        adv=adv,
        dec=dec,
        fii_today=fii_today,
        vix=vix_val,
        global_pct=global_avg_pct,
    )
    logger.info(f"Sentiment: {sentiment['label']}")

    # ── 6. Smart Money ────────────────────────────────────────
    smart_money = detect_smart_money(nifty_pct)
    logger.info("Smart money detected")

    # ── 7. Volume Shockers ────────────────────────────────────
    shockers = detect_volume_shockers(max_results=5)
    logger.info(f"Volume shockers: {len(shockers)}")

    # ── 8. News ───────────────────────────────────────────────
    news = fetch_news(max_items=6)
    logger.info(f"News fetched: {len(news)} items")

    # ── 9. Analysis text ──────────────────────────────────────
    global_cues   = generate_global_cues(market)
    nifty_outlook = generate_nifty_outlook(nifty, key_levels, adv, dec, vix_val)
    tech_note     = generate_technical_note(nifty, key_levels, fii_today, sentiment["label"])

    # ── 10. Brent sparkline ───────────────────────────────────
    sparkline = fetch_sparkline("BZ=F", days=10)
    if not sparkline:
        sparkline = [brent.get("prev_close", 95.0)] * 7 + [brent.get("val", 95.0)]

    # ── 11. Assemble ticker bar ───────────────────────────────
    ticker = _build_ticker(market)

    # ── 12. Indices table ─────────────────────────────────────
    indices = _build_indices(market)

    # ── 13. Sectors ───────────────────────────────────────────
    sectors = _build_sectors(market, nifty_pct)

    # ── 14. Date / header ─────────────────────────────────────
    date_str  = now_ist.strftime("%d %b %Y").lstrip("0")
    day_label = now_ist.strftime("%a").upper() + " · " + now_ist.strftime("%d %b %Y").upper() + " · POST-MARKET"

    # ── Assemble final payload ────────────────────────────────
    snapshot = {
        "date":     date_str,
        "dayLabel": day_label,
        "riskTags": sentiment["riskTags"],
        "ticker":   ticker,
        "keyLevels": key_levels,
        "indices":  indices,
        "advances": {"adv": adv, "dec": dec, "ratio": str(round(adv / dec, 2)) if dec else "1.0"},
        "globalCues":   global_cues,
        "niftyOutlook": nifty_outlook,
        "brentCrude": {
            "price":      brent.get("val",        95.0),
            "change":     f"{brent.get('change_pct', 0):+.2f}%",
            "changeSign": 1 if brent.get("change_pct", 0) >= 0 else -1,
            "prev":       brent.get("prev_close", 95.0),
            "prevLabel":  f"Prev: ${brent.get('prev_close', 95.0):.2f}",
            "resistance": round(brent.get("val", 95.0) * 1.08, 2),
            "note":       _brent_note(brent),
            "sparkline":  sparkline,
        },
        "optionsOI":  oi_data,
        "smartMoney": smart_money,
        "fiiDii": {
            "fii": {
                "today":    fii_dii["fii"]["today"],
                "mtdLabel": fii_dii["fii"]["mtdLabel"],
            },
            "dii": {
                "today":    fii_dii["dii"]["today"],
                "mtdLabel": fii_dii["dii"]["mtdLabel"],
            },
        },
        "results":        _placeholder_results(),   # Q4 results — static until earnings API
        "volumeShockers": shockers,
        "sectors":        sectors,
        "news":           news,
        "sentiment": {
            "label":      sentiment["label"],
            "score":      sentiment["score"],
            "confidence": sentiment["confidence"],
            "color":      sentiment["color"],
        },
        "technicalNote": tech_note,
        "_meta": {
            "generated_at": now_ist.isoformat(),
            "nifty_spot":   nifty_spot,
            "data_sources": ["yfinance", "NSE (OI)", "NSE (FII/DII)"],
        },
    }

    logger.info("Snapshot assembled successfully")
    return snapshot


# ── Helpers ───────────────────────────────────────────────────

def _avg_pct(market: dict, keys: list) -> float:
    vals = [market[k]["change_pct"] for k in keys if k in market and "change_pct" in market[k]]
    return sum(vals) / len(vals) if vals else 0.0


def _build_ticker(market: dict) -> list:
    order = ["NIFTY 50", "BANK NIFTY", "BRENT", "USDINR", "DXY", "DOW", "NASDAQ", "FTSE", "DAX"]
    ticker = []
    for label in order:
        d = market.get(label)
        if not d:
            continue
        val = d["val"]
        pct = d["change_pct"]
        # Format value
        if label in ("USDINR",):
            val_str = f"₹{val:,.2f}"
        elif label in ("BRENT",):
            val_str = f"${val:,.2f}"
        elif label in ("NIFTY 50", "BANK NIFTY"):
            val_str = f"{val:,.2f} ({pct:+.2f}%)"
        else:
            val_str = f"{val:,.2f} ({pct:+.2f}%)"
        ticker.append({
            "label": label,
            "value": val_str,
            "sign":  1 if pct >= 0 else -1,
        })
    return ticker


def _build_indices(market: dict) -> list:
    index_map = [
        ("NIFTY 50",     "NIFTY 50"),
        ("BANK NIFTY",   "BANK NIFTY"),
        ("FIN NIFTY",    "FIN NIFTY"),
        ("MIDCAP 100",   "MIDCAP 100"),
        ("SMALLCAP 100", "SMALLCAP 100"),
    ]
    indices = []
    for name, key in index_map:
        d = market.get(key)
        if not d:
            continue
        indices.append({
            "name":   name,
            "close":  f"{d['val']:,.2f}",
            "change": f"{d['change']:+.2f}",
            "pct":    f"{d['change_pct']:+.2f}%",
            "sign":   1 if d["change_pct"] >= 0 else -1,
        })
    return indices


def _build_sectors(market: dict, nifty_pct: float) -> dict:
    if nifty_pct < -1:
        title = "TOP LOSING SECTORS"
        sectors = ["IT", "Auto", "Real Estate", "Oil & Gas"]
    elif nifty_pct > 1:
        title = "SECTORS IN BUY MODE"
        sectors = ["Capital Markets", "Metals", "Energy", "Defence"]
    else:
        title = "MIXED SECTORS"
        sectors = ["FMCG", "Pharma", "IT", "Banking"]
    return {"title": title, "list": sectors}


def _brent_note(brent: dict) -> str:
    val = brent.get("val", 0)
    pct = brent.get("change_pct", 0)
    if pct > 2:
        return f"Brent surged {pct:+.1f}% to ${val:.2f}. Pressure on OMCs and paint stocks."
    elif pct < -2:
        return f"Brent fell {pct:.1f}% to ${val:.2f}. Relief for import-heavy sectors."
    else:
        return f"Brent relatively stable at ${val:.2f} ({pct:+.1f}%)."


def _placeholder_results() -> list:
    """
    Q4 results — kept as last-known data.
    In a full production system, this would be fetched from an earnings API.
    """
    return [
        {"company": "SBI",          "rev": "NII +4.15%", "np": "NP +5.6%",   "revSign": 1,  "npSign": 1},
        {"company": "MCX",          "rev": "Rev +33.6%", "np": "NP +32.1%",  "revSign": 1,  "npSign": 1},
        {"company": "Bank of Baroda","rev": "NII +9%",   "np": "NP +11.3%",  "revSign": 1,  "npSign": 1},
        {"company": "Bank of India", "rev": "NII +11%",  "np": "NP +14.8%",  "revSign": 1,  "npSign": 1},
        {"company": "Hyundai",       "rev": "Rev +5.4%", "np": "NP -22.2%",  "revSign": 1,  "npSign": -1},
        {"company": "Swiggy",        "rev": "Rev +44.7%","np": "Loss 800cr",  "revSign": 1,  "npSign": -1},
    ]
