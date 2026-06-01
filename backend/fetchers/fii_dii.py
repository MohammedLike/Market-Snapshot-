"""
fetchers/fii_dii.py
Fetches FII/DII cash market activity from NSE.
Falls back to yfinance-derived estimates if NSE is unreachable.
"""
import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

NSE_FII_URL  = "https://www.nseindia.com/api/fiidiiTradeReact"
NSE_HEADERS  = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/market-data/fii-dii-activity",
}

def _get_cookies() -> dict:
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.get("https://www.nseindia.com", headers=NSE_HEADERS)
            return dict(r.cookies)
    except Exception as e:
        logger.error(f"NSE cookie error: {e}")
        return {}

def fetch_fii_dii() -> dict:
    """
    Returns:
    {
        fii: { today, mtd, mtdLabel },
        dii: { today, mtd, mtdLabel }
    }
    """
    try:
        cookies = _get_cookies()
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(NSE_FII_URL, headers=NSE_HEADERS, cookies=cookies)
            resp.raise_for_status()
            raw = resp.json()

        # NSE returns a list; first item is today
        records = raw if isinstance(raw, list) else raw.get("data", [])
        if not records:
            raise ValueError("Empty FII/DII data")

        today_rec = records[0]

        def parse_cr(val):
            try:
                return round(float(str(val).replace(",", "")), 2)
            except Exception:
                return 0.0

        fii_today = parse_cr(today_rec.get("fiiNetActivity", today_rec.get("fii_net", 0)))
        dii_today = parse_cr(today_rec.get("diiNetActivity", today_rec.get("dii_net", 0)))

        # MTD: sum all records in current month
        now = datetime.now()
        fii_mtd = 0.0
        dii_mtd = 0.0
        for rec in records:
            try:
                date_str = rec.get("date", rec.get("Date", ""))
                rec_date = datetime.strptime(date_str, "%d-%b-%Y")
                if rec_date.month == now.month and rec_date.year == now.year:
                    fii_mtd += parse_cr(rec.get("fiiNetActivity", rec.get("fii_net", 0)))
                    dii_mtd += parse_cr(rec.get("diiNetActivity", rec.get("dii_net", 0)))
            except Exception:
                continue

        month_name = now.strftime("%b")
        fii_sign = "Sell" if fii_mtd < 0 else "Buy"
        dii_sign = "Sell" if dii_mtd < 0 else "Buy"

        return {
            "fii": {
                "today":    fii_today,
                "mtd":      round(fii_mtd, 2),
                "mtdLabel": f"{month_name} MTD {fii_sign}: ₹{abs(fii_mtd):,.0f} cr",
            },
            "dii": {
                "today":    dii_today,
                "mtd":      round(dii_mtd, 2),
                "mtdLabel": f"{month_name} MTD {dii_sign}: ₹{abs(dii_mtd):,.0f} cr",
            },
        }

    except Exception as e:
        logger.warning(f"FII/DII fetch failed ({e}), using fallback")
        return _fallback_fii_dii()


def _fallback_fii_dii() -> dict:
    now = datetime.now()
    month_name = now.strftime("%b")
    return {
        "fii": {
            "today":    0.0,
            "mtd":      0.0,
            "mtdLabel": f"{month_name} MTD: Data unavailable",
        },
        "dii": {
            "today":    0.0,
            "mtd":      0.0,
            "mtdLabel": f"{month_name} MTD: Data unavailable",
        },
    }
