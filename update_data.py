import yfinance as yf
import json
import datetime
import os
import sys

def get_market_data(target_date_str=None):
    is_live = target_date_str is None
    
    if target_date_str:
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")
        start_date = target_date.strftime("%Y-%m-%d")
        end_date = (target_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Fetching Historical Data for: {start_date}")
    else:
        target_date = datetime.datetime.now()
        print(f"Fetching LIVE Market Data...")

    # Symbols mapping
    symbols = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "BRENT": "BZ=F",
        "USDINR": "INR=X",
        "DXY": "DX-Y.NYB",
        "DOW": "^DJI",
        "NASDAQ": "^IXIC",
        "MIDCAP 100": "NIFTY_MIDCAP_100.NS", 
        "SMALLCAP 100": "^CNXSC"
    }

    results = {}
    
    for label, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            
            if is_live:
                # Use fast_info for absolute latest price during market hours
                info = ticker.fast_info
                hist = ticker.history(period="2d") # Get 2 days to calculate change
                
                if not hist.empty:
                    last_price = info['last_price']
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((last_price - prev_close) / prev_close) * 100
                    
                    results[label] = {
                        "val": last_price,
                        "change_pct": change_pct,
                        "high": info['day_high'],
                        "low": info['day_low']
                    }
            else:
                # Historical mode
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    close = hist['Close'].iloc[-1]
                    # Get previous day's close for change
                    prev_hist = ticker.history(start=(target_date - datetime.timedelta(days=5)).strftime("%Y-%m-%d"), end=start_date)
                    prev_close = prev_hist['Close'].iloc[-1] if not prev_hist.empty else hist['Open'].iloc[-1]
                    
                    change_pct = ((close - prev_close) / prev_close) * 100
                    results[label] = {
                        "val": close,
                        "change_pct": change_pct,
                        "high": hist['High'].iloc[-1],
                        "low": hist['Low'].iloc[-1]
                    }
        except Exception as e:
            print(f"Error fetching {label}: {e}")

    # Fetch News
    news_items = []
    try:
        nifty_ticker = yf.Ticker("^NSEI")
        for item in nifty_ticker.news[:3]:
            news_items.append({
                "company": "NSE",
                "headline": item['title'][:50] + "..."
            })
    except:
        pass

    # Load existing template
    json_path = "market-snapshot/src/data/marketSnapshot.json"
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Update Global Info
    data["date"] = target_date.strftime("%d %b %Y")
    data["dayLabel"] = f"{'LIVE' if is_live else 'POST-MARKET'} REPORT · {target_date.strftime('%d %b %Y').upper()}"

    if news_items:
        data["news"] = news_items

    # Update Ticker & Indices
    for item in data["ticker"]:
        lbl = item["label"]
        if lbl in results:
            val = results[lbl]["val"]
            pct = results[lbl]["change_pct"]
            item["value"] = f"{val:,.2f} ({pct:+.2f}%)"
            item["sign"] = 1 if pct >= 0 else -1

    for idx in data["indices"]:
        name = idx["name"]
        if name in results:
            idx["close"] = f"{results[name]['val']:,.2f}"
            idx["pct"] = f"{results[name]['change_pct']:+.2f}%"
            idx["sign"] = 1 if results[name]['change_pct'] >= 0 else -1

    if "NIFTY 50" in results:
        nifty = results["NIFTY 50"]
        data["keyLevels"]["currentPrice"] = int(nifty["val"])
        # Frame the range bar dynamically
        data["keyLevels"]["min"] = int(nifty["val"] - 400)
        data["keyLevels"]["max"] = int(nifty["val"] + 400)

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Success: Updated with {'Latest LIVE' if is_live else start_date} values.")


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    get_market_data(date_arg)
