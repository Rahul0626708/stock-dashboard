import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional

# ── App setup ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Stock Data Intelligence API",
    description="Mini financial platform — NSE stock data, metrics & insights",
    version="1.0.0"
)

# Allow frontend dashboard to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_PATH = "stocks.db"

# ── Helper: load data from SQLite ──────────────────────────────────────
def load(symbol: str = None) -> pd.DataFrame:
    """Load stock data from DB. Filter by symbol if provided."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM stocks"
    if symbol:
        query += f" WHERE symbol = '{symbol.upper()}'"
    df = pd.read_sql(query, conn, parse_dates=["date"])
    conn.close()
    return df.sort_values("date").reset_index(drop=True)

# ── ENDPOINT 1: GET /companies ─────────────────────────────────────────
@app.get("/companies", summary="List all available stock symbols")
def get_companies():
    """Returns the list of all companies in the database."""
    df = load()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found. Run data_collector.py first.")
    companies = df["symbol"].unique().tolist()
    return {
        "count": len(companies),
        "companies": companies
    }

# ── ENDPOINT 2: GET /data/{symbol} ────────────────────────────────────
@app.get("/data/{symbol}", summary="Get stock data for a symbol")
def get_stock_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days (1-365)")
):
    """
    Returns OHLCV data + calculated metrics for the given symbol.
    Use ?days=90 for last 90 days, ?days=252 for full year.
    """
    df = load(symbol)
    if df.empty:
        raise HTTPException(status_code=404,
            detail=f"Symbol '{symbol.upper()}' not found. Available: TCS, INFY, RELIANCE, HDFCBANK, WIPRO")
    df = df.tail(days)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return {
        "symbol": symbol.upper(),
        "days_returned": len(df),
        "data": df.to_dict(orient="records")
    }

# ── ENDPOINT 3: GET /summary/{symbol} ─────────────────────────────────
@app.get("/summary/{symbol}", summary="52-week stats summary")
def get_summary(symbol: str):
    """
    Returns 52-week high, low, average close price,
    latest volatility score, and momentum index.
    """
    df = load(symbol)
    if df.empty:
        raise HTTPException(status_code=404,
            detail=f"Symbol '{symbol.upper()}' not found.")
    latest = df.iloc[-1]
    return {
        "symbol":          symbol.upper(),
        "high_52w":        round(float(df["close"].max()), 2),
        "low_52w":         round(float(df["close"].min()), 2),
        "avg_close":       round(float(df["close"].mean()), 2),
        "latest_close":    round(float(latest["close"]), 2),
        "daily_return_pct":round(float(latest["daily_return"]) * 100, 3),
        "volatility_score":round(float(latest["volatility"]), 6),
        "momentum_index":  round(float(latest["momentum"]), 2),
        "total_trading_days": len(df)
    }

# ── ENDPOINT 4: GET /compare ───────────────────────────────────────────
@app.get("/compare", summary="Compare two stocks side by side")
def compare_stocks(
    symbol1: str = Query(..., example="TCS",  description="First stock symbol"),
    symbol2: str = Query(..., example="INFY", description="Second stock symbol")
):
    """
    Compare performance of two stocks.
    Example: /compare?symbol1=TCS&symbol2=INFY
    """
    result = {}
    for sym in [symbol1, symbol2]:
        df = load(sym)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Symbol '{sym}' not found.")
        latest = df.iloc[-1]
        result[sym.upper()] = {
            "latest_close":    round(float(latest["close"]), 2),
            "high_52w":        round(float(df["close"].max()), 2),
            "low_52w":         round(float(df["close"].min()), 2),
            "avg_daily_return":round(float(df["daily_return"].mean()) * 100, 3),
            "volatility":      round(float(df["daily_return"].std()), 6),
            "momentum_index":  round(float(latest["momentum"]), 2),
            "trend": "Bullish 📈" if float(latest["momentum"]) > 100 else "Bearish 📉"
        }
    return {"comparison": result,
            "winner_by_return": max(result, key=lambda k: result[k]["avg_daily_return"])}

# ── ENDPOINT 5: GET /top-gainers  (BONUS) ─────────────────────────────
@app.get("/top-gainers", summary="Top 3 stocks by daily return (bonus)")
def top_gainers():
    """Returns the top 3 performing stocks based on most recent daily return."""
    df = load()
    latest_date = df["date"].max()
    today_df = df[df["date"] == latest_date].copy()
    today_df["daily_return_pct"] = (today_df["daily_return"] * 100).round(2)
    top3 = today_df.nlargest(3, "daily_return")[
        ["symbol", "close", "daily_return_pct"]
    ]
    return {
        "date": str(latest_date)[::10],
        "top_gainers": top3.to_dict(orient="records")
    }

# ── Root: redirect to docs ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return """<meta http-equiv="refresh" content="0;url=/docs">"""
# ── BONUS 1: GET /correlation ──────────────────────────────────
@app.get("/correlation", summary="Pearson correlation matrix between all stocks")
def get_correlation():
    """
    Shows how correlated each pair of stocks is based on daily returns.
    1.0 = move perfectly together, -1.0 = move opposite, 0 = no relation.
    """
    df = load()
    pivot = df.pivot_table(
        index="date", columns="symbol", values="daily_return"
    )
    corr = pivot.corr().round(4)
    return {
        "description": "Pearson correlation of daily returns",
        "note": "1.0=perfect match  0=no relation  -1.0=opposite",
        "matrix": corr.to_dict()
    }

# ── BONUS 2: GET /predict/{symbol} ─────────────────────────────
@app.get("/predict/{symbol}", summary="7-day price prediction using ML")
def predict_price(symbol: str):
    """
    Linear regression on last 60 days to predict next 7 trading days.
    Disclaimer: Educational only — not financial advice.
    """
    df = load(symbol)
    if df.empty:
        raise HTTPException(404, detail=f"Symbol '{symbol}' not found.")

    recent = df.tail(60).reset_index(drop=True)
    X = recent.index.values.reshape(-1, 1)
    y = recent["close"].values

    model = LinearRegression()
    model.fit(X, y)

    last_idx = len(recent)
    preds = model.predict(np.arange(last_idx, last_idx + 7).reshape(-1, 1))
    last_close = float(recent["close"].iloc[-1])

    return {
        "symbol": symbol.upper(),
        "model": "Linear Regression (trained on last 60 trading days)",
        "current_close": round(last_close, 2),
        "disclaimer": "Educational only. Not financial advice.",
        "predictions": [
            {
                "day": f"Day +{i+1}",
                "predicted_close": round(float(p), 2),
                "change_pct": round((float(p) - last_close) / last_close * 100, 2)
            }
            for i, p in enumerate(preds)
        ]
    }