import sqlite3
import pandas as pd

conn = sqlite3.connect("stocks.db")
df   = pd.read_sql("SELECT * FROM stocks", conn)
conn.close()

print("📊 DATABASE SUMMARY")
print(f"   Total rows   : {len(df)}")
print(f"   Companies    : {df['symbol'].unique().tolist()}")
print(f"   Columns      : {list(df.columns)}")
print(f"   Date range   : {df['date'].min()} → {df['date'].max()}")

print("📈 SAMPLE — TCS last 5 rows:")
tcs = df[df['symbol'] == 'TCS'].tail(5)
print(tcs[['date', 'open', 'close',
           'daily_return', 'ma_7',
           'volatility', 'momentum']].to_string(index=False))

print("✅ All good! Run main.py tomorrow for the API.")