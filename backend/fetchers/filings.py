import httpx
import logging
import re
from datetime import datetime, date
import pytz
import yfinance as yf

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

# ── NSE Announcements ─────────────────────────────────────────
NSE_ANNOUNCEMENTS_URL = (
    "https://www.nseindia.com/api/corporate-announcements"
    "?index=equities&from_date={from_date}&to_date={to_date}"
)
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
}

# ── BSE Announcements ─────────────────────────────────────────
BSE_ANNOUNCEMENTS_URL = (
    "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    "?pageno=1&strCat=-1&strPrevDate={from_date}&strScrip=&strSearch=P"
    "&strToDate={to_date}&strType=C&subcategory=-1"
)
BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.bseindia.com/corporates/ann.html",
}

# Filing types we care about — ordered by priority
PRIORITY_TYPES = [
    "Financial Results",
    "Board Meeting",
    "Dividend",
    "Bonus",
    "Rights Issue",
    "Merger",
    "Acquisition",
    "Buyback",
    "Insider Trading",
    "Shareholding Pattern",
]

# Colour signals for the badge columns
_POSITIVE_KEYWORDS = {
    "dividend", "bonus", "buyback", "profit", "growth",
    "acquisition", "rights", "record date",
}
_NEGATIVE_KEYWORDS = {
    "loss", "default", "penalty", "fraud", "insolvency",
    "winding", "suspension", "delisting",
}


def _get_nse_cookies() -> dict:
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as c:
            r = c.get("https://www.nseindia.com", headers=NSE_HEADERS)
            return dict(r.cookies)
    except Exception as e:
        logger.debug(f"NSE cookie error: {e}")
        return {}


def _sign_from_text(text: str) -> int:
    t = text.lower()
    if any(k in t for k in _POSITIVE_KEYWORDS):
        return 1
    if any(k in t for k in _NEGATIVE_KEYWORDS):
        return -1
    return 0   # neutral → grey badge


def _short_subject(subject: str, max_len: int = 28) -> str:
    """Trim and clean a filing subject line."""
    s = re.sub(r"\s+", " ", subject).strip()
    return s if len(s) <= max_len else s[:max_len - 1] + "…"


def _format_time(dt_str: str) -> str:
    """Try to extract HH:MM from various datetime string formats."""
    for fmt in ("%d-%b-%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S",
                "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            return dt.strftime("%I:%M %p")
        except ValueError:
            continue
    return ""


# ── NSE fetch ─────────────────────────────────────────────────
def _fetch_nse(today_str: str) -> list[dict]:
    url = NSE_ANNOUNCEMENTS_URL.format(from_date=today_str, to_date=today_str)
    cookies = _get_nse_cookies()
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as c:
            r = c.get(url, headers=NSE_HEADERS, cookies=cookies)
            r.raise_for_status()
            raw = r.json()
    except Exception as e:
        logger.warning(f"NSE filings fetch failed: {e}")
        return []

    items = raw if isinstance(raw, list) else raw.get("data", [])
    results = []
    for item in items:
        company = (item.get("symbol") or item.get("sm_name") or "").strip()
        subject = (item.get("subject") or item.get("desc") or "").strip()
        dt_str  = (item.get("an_dt") or item.get("date") or "").strip()
        if not company or not subject:
            continue
        results.append({
            "company": company[:18],
            "subject": subject,
            "time":    _format_time(dt_str),
            "source":  "NSE",
        })
    return results


# ── BSE fetch ─────────────────────────────────────────────────
def _fetch_bse(today_str: str) -> list[dict]:
    # BSE expects DD/MM/YYYY
    try:
        d = datetime.strptime(today_str, "%d-%m-%Y")
        bse_date = d.strftime("%d/%m/%Y")
    except ValueError:
        bse_date = today_str

    url = BSE_ANNOUNCEMENTS_URL.format(from_date=bse_date, to_date=bse_date)
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as c:
            r = c.get(url, headers=BSE_HEADERS)
            r.raise_for_status()
            raw = r.json()
    except Exception as e:
        logger.warning(f"BSE filings fetch failed: {e}")
        return []

    items = raw.get("Table", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []

    results = []
    for item in items:
        company = (item.get("SLONGNAME") or item.get("scrip_cd") or "").strip()
        subject = (item.get("HEADLINE") or item.get("CATEGORYNAME") or "").strip()
        dt_str  = (item.get("NEWS_DT") or item.get("DissemDT") or "").strip()
        if not company or not subject:
            continue
        results.append({
            "company": company[:18],
            "subject": subject,
            "time":    _format_time(dt_str),
            "source":  "BSE",
        })
    return results


# ── yfinance fallback ─────────────────────────────────────────
def _fetch_yfinance_earnings() -> list[dict]:
    """
    Pull earnings-related news from top Nifty stocks as last resort.
    """
    SYMBOLS = [
        ("RELIANCE",  "RELIANCE.NS"), ("HDFCBANK", "HDFCBANK.NS"),
        ("INFY",      "INFY.NS"),     ("TCS",      "TCS.NS"),
        ("ICICIBANK", "ICICIBANK.NS"),("SBIN",     "SBIN.NS"),
        ("WIPRO",     "WIPRO.NS"),    ("AXISBANK", "AXISBANK.NS"),
    ]
    EARNINGS_KEYWORDS = {
        "result", "earnings", "profit", "revenue", "quarterly",
        "q1", "q2", "q3", "q4", "annual", "dividend", "board meeting",
    }
    results = []
    seen = set()
    for name, sym in SYMBOLS:
        if len(results) >= 8:
            break
        try:
            t = yf.Ticker(sym)
            for item in (t.news or []):
                title = (item.get("title") or "").strip()
                if not title or title in seen:
                    continue
                if not any(k in title.lower() for k in EARNINGS_KEYWORDS):
                    continue
                seen.add(title)
                results.append({
                    "company": name,
                    "subject": title,
                    "time":    "",
                    "source":  "yfinance",
                })
                break
        except Exception:
            pass
    return results


# ── Priority filter ───────────────────────────────────────────
def _prioritise(items: list[dict], max_items: int) -> list[dict]:
    """
    Sort by priority type keywords, deduplicate by company,
    return top max_items.
    """
    def priority_score(item):
        subj = item["subject"].lower()
        for i, kw in enumerate(PRIORITY_TYPES):
            if kw.lower() in subj:
                return i
        return len(PRIORITY_TYPES)

    seen_companies = set()
    unique = []
    for item in sorted(items, key=priority_score):
        key = item["company"].upper()
        if key not in seen_companies:
            seen_companies.add(key)
            unique.append(item)
        if len(unique) >= max_items:
            break
    return unique


# ── Schema converter ──────────────────────────────────────────
def _to_results_schema(items: list[dict]) -> list[dict]:
    """
    Convert raw filing items to the ResultsBoard schema:
      company, rev (filing type), np (time/detail), revSign, npSign
    """
    out = []
    for item in items:
        subj     = item["subject"]
        time_str = item["time"] or item["source"]
        rev_sign = _sign_from_text(subj)
        out.append({
            "company": item["company"],
            "rev":     _short_subject(subj, 26),
            "np":      time_str[:14],
            "revSign": rev_sign,
            "npSign":  0,   # time column always neutral
        })
    return out


# ── Public API ────────────────────────────────────────────────
def fetch_today_filings(max_items: int = 8) -> list[dict]:
    """
    Main entry point. Returns today's filings in ResultsBoard schema.
    Tries NSE → BSE → yfinance in order, merges and deduplicates.
    """
    now_ist   = datetime.now(IST)
    today_str = now_ist.strftime("%d-%m-%Y")   # NSE format

    logger.info(f"Fetching filings for {today_str}")

    # Collect from all sources
    nse_items = _fetch_nse(today_str)
    logger.info(f"NSE filings: {len(nse_items)}")

    bse_items = _fetch_bse(today_str)
    logger.info(f"BSE filings: {len(bse_items)}")

    combined = nse_items + bse_items

    # Fall back to yfinance if both exchanges returned nothing
    if not combined:
        logger.warning("NSE + BSE returned no filings, falling back to yfinance")
        combined = _fetch_yfinance_earnings()

    if not combined:
        logger.warning("All filing sources failed — returning placeholder")
        return _fallback_filings()

    top = _prioritise(combined, max_items)
    return _to_results_schema(top)


def _fallback_filings() -> list[dict]:
    return [
        {"company": "NSE",  "rev": "No filings today", "np": "", "revSign": 0, "npSign": 0},
        {"company": "BSE",  "rev": "Check exchange site", "np": "", "revSign": 0, "npSign": 0},
    ]
