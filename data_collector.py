import yfinance as yf
import pandas as pd
import sqlite3
import os

# ── 5 NSE stocks we are tracking ──────────────────────────────
SYMBOLS = [
    "TCS.NS",       # Tata Consultancy Services
    "INFY.NS",      # Infosys
    "RELIANCE.NS",  # Reliance Industries
    "HDFCBANK.NS",  # HDFC Bank
    "WIPRO.NS",     # Wipro
]
DB_PATH = "stocks.db"

def clean_and_enrich(df, symbol):
    """Clean raw yfinance data and add calculated metrics."""
    df = df.copy()
    df.reset_index(inplace=True)

    # Flatten MultiIndex columns (yfinance sometimes returns these)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # Make sure date column is correct
    date_col = 'datetime' if 'datetime' in df.columns else 'date'
    df.rename(columns={date_col: 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    # Add stock symbol (without .NS)
    df['symbol'] = symbol.replace('.NS', '')

    # Drop rows where OHLC data is missing
    df.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)
    df = df.sort_values('date').reset_index(drop=True)

    # ── METRIC 1: Daily Return = (Close - Open) / Open ────────────
    df['daily_return'] = (df['close'] - df['open']) / df['open']

    # ── METRIC 2: Moving Averages ──────────────────────────────────
    df['ma_7']  = df['close'].rolling(window=7).mean().round(2)
    df['ma_30'] = df['close'].rolling(window=30).mean().round(2)

    # ── METRIC 3: 52-Week High and Low ────────────────────────────
    df['high_52w'] = round(df['close'].max(), 2)
    df['low_52w']  = round(df['close'].min(), 2)

    # ── METRIC 4: Volatility Score (30-day rolling std) ───────────
    df['volatility'] = df['daily_return'].rolling(window=30).std().round(6)

    # ── METRIC 5: Momentum Index ───────────────────────────────────
    # (Current Price / Price 30 days ago) x 100
    # >100 = bullish, <100 = bearish
    df['momentum'] = ((df['close'] / df['close'].shift(30)) * 100).round(2)

    # Fill NaN values created by rolling windows
    df.ffill(inplace=True)
    df.bfill(inplace=True)

    return df

def fetch_and_store():
    """Fetch all 5 stocks and store to SQLite database."""

    # Start fresh each time
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed old stocks.db — starting fresh")

    conn = sqlite3.connect(DB_PATH)
    total_rows = 0

    for symbol in SYMBOLS:
        print(f"Fetching {symbol}...", end=" ")
        try:
            raw = yf.download(symbol, period="1y",
                              auto_adjust=True, progress=False)
            if raw.empty:
                print("WARNING: no data returned")
                continue

            df = clean_and_enrich(raw, symbol)
            df.to_sql("stocks", conn,
                      if_exists="append", index=False)
            total_rows += len(df)
            print(f"✓ {len(df)} rows saved")

        except Exception as e:
            print(f"ERROR: {e}")

    conn.close()
    print(f"{'='*45}")
    print(f"✅ DONE! {total_rows} total rows in stocks.db")
    print(f"📁 Location: {os.path.abspath(DB_PATH)}")
    print(f"{'='*45}")
    print("Next: run  python verify_data.py")

if __name__ == "__main__":
    fetch_and_store()