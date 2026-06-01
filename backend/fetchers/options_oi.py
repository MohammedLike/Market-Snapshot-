"""
fetchers/options_oi.py
Fetches Nifty options chain from NSE (unofficial) and calculates:
  - Top 3 Call OI strikes (resistance)
  - Top 3 Put OI strikes (support)
  - Call Wall, Put Floor, Max Pain, PCR
"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

NSE_OPTION_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

def _get_nse_session_cookies() -> dict:
    """NSE requires a session cookie from the main page first."""
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.get("https://www.nseindia.com", headers=NSE_HEADERS)
            return dict(r.cookies)
    except Exception as e:
        logger.error(f"NSE cookie fetch failed: {e}")
        return {}

def fetch_options_oi(spot_price: float) -> dict:
    """
    Returns structured OI data for the frontend.
    Falls back to ATM-based synthetic data if NSE is unreachable.
    """
    try:
        cookies = _get_nse_session_cookies()
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(NSE_OPTION_CHAIN_URL, headers=NSE_HEADERS, cookies=cookies)
            resp.raise_for_status()
            raw = resp.json()

        records = raw.get("records", {}).get("data", [])
        if not records:
            raise ValueError("Empty option chain data")

        # Aggregate OI by strike
        call_oi = {}
        put_oi  = {}

        for rec in records:
            strike = rec.get("strikePrice", 0)
            ce = rec.get("CE", {})
            pe = rec.get("PE", {})
            if ce:
                call_oi[strike] = call_oi.get(strike, 0) + ce.get("openInterest", 0)
            if pe:
                put_oi[strike]  = put_oi.get(strike, 0)  + pe.get("openInterest", 0)

        return _build_oi_payload(call_oi, put_oi, spot_price)

    except Exception as e:
        logger.warning(f"NSE OI fetch failed ({e}), using synthetic fallback")
        return _synthetic_oi(spot_price)


def _build_oi_payload(call_oi: dict, put_oi: dict, spot: float) -> dict:
    """Derive all OI metrics from raw strike→OI maps."""
    if not call_oi or not put_oi:
        return _synthetic_oi(spot)

    # Sort by OI descending, take top 3 above/below spot
    top_calls = sorted(
        [(k, v) for k, v in call_oi.items() if k >= spot],
        key=lambda x: x[1], reverse=True
    )[:3]
    top_puts = sorted(
        [(k, v) for k, v in put_oi.items() if k <= spot],
        key=lambda x: x[1], reverse=True
    )[:3]

    max_call_oi = max(call_oi.values()) if call_oi else 1
    max_put_oi  = max(put_oi.values())  if put_oi  else 1

    def level_label(pct):
        if pct >= 90: return "MAX"
        if pct >= 65: return "High"
        if pct >= 40: return "Med"
        return "Low"

    call_rows = [
        {
            "strike": int(s),
            "level":  level_label(int(oi / max_call_oi * 100)),
            "pct":    int(oi / max_call_oi * 100),
        }
        for s, oi in sorted(top_calls, key=lambda x: x[0])
    ]
    put_rows = [
        {
            "strike": int(s),
            "level":  level_label(int(oi / max_put_oi * 100)),
            "pct":    int(oi / max_put_oi * 100),
        }
        for s, oi in sorted(top_puts, key=lambda x: x[0], reverse=True)
    ]

    # Call Wall = highest OI call strike
    call_wall  = max(call_oi, key=call_oi.get) if call_oi else int(spot + 200)
    put_floor  = max(put_oi,  key=put_oi.get)  if put_oi  else int(spot - 200)

    # PCR
    total_call = sum(call_oi.values())
    total_put  = sum(put_oi.values())
    pcr = round(total_put / total_call, 2) if total_call else 1.0

    # Max Pain — strike where total loss for option buyers is maximum
    max_pain = _calc_max_pain(call_oi, put_oi)

    # OI title
    if pcr < 0.8:
        title = "Heavy Call Writing"
    elif pcr > 1.2:
        title = "Heavy Put Writing"
    else:
        title = "Balanced OI"

    note = (
        f"PCR: {pcr:.2f} | Max Pain: {max_pain:,} | "
        f"Call Wall at {call_wall:,} | Put Floor at {put_floor:,}"
    )

    return {
        "title":    title,
        "callOI":   call_rows,
        "putOI":    put_rows,
        "callWall": int(call_wall),
        "putFloor": int(put_floor),
        "pcr":      pcr,
        "maxPain":  int(max_pain),
        "note":     note,
    }


def _calc_max_pain(call_oi: dict, put_oi: dict) -> float:
    """Standard max pain calculation."""
    all_strikes = sorted(set(list(call_oi.keys()) + list(put_oi.keys())))
    if not all_strikes:
        return 0

    min_loss = float("inf")
    max_pain_strike = all_strikes[0]

    for expiry in all_strikes:
        total_loss = 0
        for s, oi in call_oi.items():
            if expiry > s:
                total_loss += (expiry - s) * oi
        for s, oi in put_oi.items():
            if expiry < s:
                total_loss += (s - expiry) * oi
        if total_loss < min_loss:
            min_loss = total_loss
            max_pain_strike = expiry

    return max_pain_strike


def _synthetic_oi(spot: float) -> dict:
    """ATM-based synthetic OI when NSE is unreachable."""
    base = round(spot / 50) * 50  # round to nearest 50

    call_rows = [
        {"strike": int(base + 100), "level": "Med",  "pct": 55},
        {"strike": int(base + 200), "level": "High", "pct": 75},
        {"strike": int(base + 300), "level": "MAX",  "pct": 95},
    ]
    put_rows = [
        {"strike": int(base - 100), "level": "Low",  "pct": 30},
        {"strike": int(base - 200), "level": "Med",  "pct": 55},
        {"strike": int(base - 300), "level": "MAX",  "pct": 90},
    ]
    return {
        "title":    "OI Data (Estimated)",
        "callOI":   call_rows,
        "putOI":    put_rows,
        "callWall": int(base + 300),
        "putFloor": int(base - 300),
        "pcr":      1.0,
        "maxPain":  int(base),
        "note":     "Live OI unavailable. Showing ATM-based estimates.",
    }
