# 📈 Stock Data Intelligence Dashboard

> Built with **Python · FastAPI · SQLite · Chart.js**
> Real NSE stock data · REST API · Swagger UI · Dark-mode Dashboard · ML Prediction

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/stock-dashboard.git
cd stock-dashboard
pip install -r requirements.txt
python data_collector.py        # fetch & store stock data
uvicorn main:app --reload --port 8000   # start API
# Then open dashboard.html in your browser
```

---

## 📁 Project Structure

```
stock-dashboard/
├── data_collector.py   ← Fetches & stores real NSE stock data
├── main.py             ← FastAPI REST API (7 endpoints)
├── dashboard.html      ← Interactive dark-mode frontend
├── stocks.db           ← SQLite database (auto-generated)
├── requirements.txt    ← Python dependencies
├── Dockerfile          ← Docker containerization
└── README.md           ← This file
```

---

## ⚙️ Tech Stack

| Layer    | Tech                 | Purpose                            |
| -------- | -------------------- | ---------------------------------- |
| Language | Python 3.10+         | Data processing & API logic        |
| Backend  | FastAPI + Uvicorn    | REST API + auto Swagger UI docs    |
| Data     | Pandas + yfinance    | Fetch & transform NSE stock data   |
| Database | SQLite               | Lightweight file-based storage     |
| Frontend | HTML + JS + Chart.js | Single-file interactive dashboard  |
| ML       | scikit-learn         | Linear regression price prediction |

---

## 📊 API Endpoints

Swagger UI: `http://localhost:8000/docs`

| Method | Endpoint                            | Description                    |
| ------ | ----------------------------------- | ------------------------------ |
| GET    | `/companies`                        | List all tracked stock symbols |
| GET    | `/data/{symbol}?days=30`            | OHLCV + metrics for N days     |
| GET    | `/summary/{symbol}`                 | 52-week stats + custom metrics |
| GET    | `/compare?symbol1=TCS&symbol2=INFY` | Side-by-side stock comparison  |
| GET    | `/top-gainers`                      | Top 3 stocks by daily return   |
| GET    | `/correlation`                      | Pearson correlation matrix ⭐  |
| GET    | `/predict/{symbol}`                 | 7-day ML price prediction ⭐   |

### Sample Response — `/summary/TCS`

```json
{
  "symbol": "TCS",
  "high_52w": 4592.5,
  "low_52w": 3311.25,
  "avg_close": 3987.4,
  "latest_close": 3854.2,
  "volatility_score": 0.009214,
  "momentum_index": 101.34,
  "total_trading_days": 247
}
```

---

## 🧠 Custom Metrics

### 1. Daily Return

```
Daily Return = (Close − Open) / Open
```

How much the stock gained or lost in a single trading day.

### 2. Moving Averages (7-day & 30-day)

Rolling mean of closing price. Smooths noise to reveal trend direction.

### 3. Volatility Score ⭐ (Custom)

```
Volatility = 30-day rolling standard deviation of Daily Returns
```

Higher = more unpredictable = higher risk. Used by real analysts.

### 4. Momentum Index ⭐ (Custom)

```
Momentum = (Current Price / Price 30 days ago) × 100
```

- **> 100** → Bullish 📈
- **< 100** → Bearish 📉

### 5. 52-Week High / Low

Highest and lowest closing price over the past year.

---

## 🏢 Stocks Tracked

| Symbol   | Company                   | Sector       |
| -------- | ------------------------- | ------------ |
| TCS      | Tata Consultancy Services | IT           |
| INFY     | Infosys                   | IT           |
| RELIANCE | Reliance Industries       | Conglomerate |
| HDFCBANK | HDFC Bank                 | Banking      |
| WIPRO    | Wipro                     | IT           |

---

## 🎨 Dashboard Features

- Dark-mode professional UI
- Company sidebar — click any stock to load chart
- Closing price + 7-day MA overlay (Chart.js)
- Stats cards: 52W High/Low, Volatility, Momentum (Bullish/Bearish)
- Time filters: 30D / 90D / 1Y
- Top Gainers widget
- Live IST clock

---

## 🐳 Docker

```bash
docker build -t stock-dashboard .
docker run -p 8000:8000 stock-dashboard
```

---

## 👤 Author

**[YOUR NAME]**
Internship Assignment — Jarnox

_Data via Yahoo Finance (yfinance). Educational purposes only._
