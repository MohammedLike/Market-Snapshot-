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
from fetchers.filings        import fetch_today_filings
from fetchers.breadth        import fetch_market_breadth
from fetchers.heatmap        import fetch_sector_heatmap
from fetchers.institutional    import fetch_fii_index_ratio, fetch_delivery_data
from fetchers.events           import fetch_economic_calendar, calculate_global_alignment
from analytics.key_levels    import calculate_key_levels
from analytics.smart_money   import detect_smart_money
from analytics.sentiment     import calculate_sentiment
from analytics.volume_shockers import detect_volume_shockers
from analytics.technical_indicators import calculate_indicators, get_vix_correlation
from analytics.market_mood         import generate_ai_mood
from analytics.market_analysis import (
    generate_global_cues,
    generate_nifty_outlook,
    generate_technical_note,
)

logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ── Filings cache (5-minute TTL, separate from main 60s cache) ──
import time as _time
_filings_cache: dict = {"data": None, "ts": 0}
_FILINGS_TTL = 5 * 60   # 5 minutes

def _get_filings() -> list:
    """Returns cached filings or fetches fresh ones if TTL expired."""
    now = _time.time()
    if _filings_cache["data"] is None or (now - _filings_cache["ts"]) > _FILINGS_TTL:
        logger.info("Filings cache expired — fetching fresh filings")
        _filings_cache["data"] = fetch_today_filings(max_items=8)
        _filings_cache["ts"]   = now
    else:
        logger.info("Filings cache hit")
    return _filings_cache["data"]


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
    breadth = fetch_market_breadth()
    adv = breadth["adv"]
    dec = breadth["dec"]
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

    # ── 7b. Sector Heatmap ────────────────────────────────────
    heatmap = fetch_sector_heatmap()
    logger.info(f"Heatmap: {len(heatmap)} sectors")

    # ── 7c. Technical Metrics (DMA/RSI) ──────────────────────
    tech_symbols = ["^NSEI", "^NSEBANK", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    tech_indicators = calculate_indicators(tech_symbols)
    vix_corr = get_vix_correlation()
    logger.info("Technical indicators & VIX correlation calculated")

    # ── 7d. Institutional Pro Data ───────────────────────────
    fii_ratio = fetch_fii_index_ratio()
    delivery_stats = fetch_delivery_data(["RELIANCE", "HDFCBANK", "TCS", "INFY", "ITC"])
    logger.info("Institutional pro data fetched")

    # ── 7e. Events & Macro ───────────────────────────────────
    events = fetch_economic_calendar()
    alignment = calculate_global_alignment(market)
    logger.info("Economic events and global alignment fetched")

    # ── 7f. AI Market Mood ───────────────────────────────────
    # Initial temporary payload to pass to generator
    temp_data = {
        "ticker": ticker,
        "fiiRatio": fii_ratio,
        "advances": breadth,
        "niftyOutlook": {"levels": [{"value": "15"}]} # placeholder for VIX
    }
    ai_mood = generate_ai_mood(temp_data)
    logger.info(f"AI Mood generated: {ai_mood['headline']}")

    # ── 8. News (Corporate Announcements) ────────────────────
    filings = _get_filings()
    news = [
        {"company": f["company"], "headline": f["rev"]}
        for f in filings[:6]
    ]
    if not news:
        news = fetch_news(max_items=6)
    
    logger.info(f"News (Filings): {len(news)} items")

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
        "advances": breadth,
        "globalCues":   global_cues,
        "niftyOutlook": generate_nifty_outlook(nifty, key_levels, adv, dec, vix_val),
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
        "results":        filings,
        "volumeShockers": shockers,
        "sectors":        sectors,
        "heatmap":        heatmap,
        "technicalMetrics": tech_indicators,
        "vixCorrelation": vix_corr,
        "fiiRatio":       fii_ratio,
        "deliveryStats":  delivery_stats,
        "events":         events,
        "globalAlignment": alignment,
        "aiMood":          ai_mood,
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
            "data_sources": ["yfinance", "NSE (OI)", "NSE (FII/DII)", "NSE/BSE (Filings)"],
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



