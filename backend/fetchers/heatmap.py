"""
fetchers/heatmap.py
Fetches sector-wise stock performance for the heatmap.
"""
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

SECTOR_MAP = {
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "Auto": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"],
    "Energy": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS"],
    "Metals": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "VEDL.NS"],
    "Pharma": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS"],
}

def fetch_sector_heatmap() -> list:
    """
    Returns sector performance data for a treemap-style heatmap.
    """
    all_symbols = [s for stocks in SECTOR_MAP.values() for s in stocks]
    try:
        data = yf.download(
            all_symbols,
            period="2d",
            interval="1d",
            group_by="ticker",
            progress=False,
            threads=True,
            auto_adjust=True
        )
        
        heatmap = []
        for sector, stocks in SECTOR_MAP.items():
            sector_val = 0
            count = 0
            stock_data = []
            
            for symbol in stocks:
                try:
                    if symbol not in data.columns.get_level_values(0):
                        continue
                    df = data[symbol].dropna()
                    if len(df) < 2:
                        continue
                        
                    close = df['Close'].iloc[-1]
                    prev  = df['Close'].iloc[-2]
                    pct   = round(((close - prev) / prev * 100), 2)
                    
                    stock_data.append({
                        "name": symbol.replace(".NS", ""),
                        "value": pct
                    })
                    sector_val += pct
                    count += 1
                except Exception:
                    continue
            
            if count > 0:
                heatmap.append({
                    "name": sector,
                    "value": round(sector_val / count, 2),
                    "children": stock_data
                })
                
        return heatmap
    except Exception as e:
        logger.error(f"Heatmap fetch failed: {e}")
        return []
