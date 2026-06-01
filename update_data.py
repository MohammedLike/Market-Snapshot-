import yfinance as yf
import json
import datetime
import os
import sys

def get_market_data(target_date_str=None):
    # If no date provided, use yesterday (EOD)
    if target_date_str:
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")
    else:
        target_date = datetime.datetime.now() - datetime.timedelta(days=1)
    
    start_date = target_date.strftime("%Y-%m-%d")
    end_date = (target_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Fetching data for: {start_date}")

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
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                # Try getting last available if specific date failed
                hist = ticker.history(period="1d")
            
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                prev_close = hist['Open'].iloc[-1] # Simplification for change calc
                
                # For more accurate prev close, we'd need another fetch, 
                # but yfinance period='1d' usually has enough.
                # Let's try to get actual change if possible
                info = ticker.fast_info
                change_pct = ((close - prev_close) / prev_close) * 100
                
                results[label] = {
                    "val": close,
                    "change_pct": change_pct,
                    "high": hist['High'].iloc[-1],
                    "low": hist['Low'].iloc[-1]
                }
        except Exception as e:
            print(f"Error fetching {label}: {e}")

    # Load existing template to preserve structure
    json_path = "market-snapshot/src/data/marketSnapshot.json"
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Update Date
    data["date"] = target_date.strftime("%d %b %Y")
    data["dayLabel"] = f"POST-MARKET CLOSING · {target_date.strftime('%d %b %Y').upper()}"

    # Update Ticker
    for item in data["ticker"]:
        lbl = item["label"]
        if lbl in results:
            val = results[lbl]["val"]
            pct = results[lbl]["change_pct"]
            item["value"] = f"{val:,.2f} ({pct:+.2f}%)"
            item["sign"] = 1 if pct >= 0 else -1

    # Update Indices Close
    for idx in data["indices"]:
        name = idx["name"]
        if name in results:
            idx["close"] = f"{results[name]['val']:,.2f}"
            idx["pct"] = f"{results[name]['change_pct']:+.2f}%"
            idx["sign"] = 1 if results[name]['change_pct'] >= 0 else -1

    # Update Key Levels current price and range
    if "NIFTY 50" in results:
        nifty = results["NIFTY 50"]
        data["keyLevels"]["currentPrice"] = int(nifty["val"])
        # Adjust min/max to frame the current price nicely
        data["keyLevels"]["min"] = int(nifty["val"] // 1000 * 1000)
        data["keyLevels"]["max"] = data["keyLevels"]["min"] + 1000

    # Save back
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully updated dashboard with {start_date} data.")

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    get_market_data(date_arg)
