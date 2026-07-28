import pandas as pd
from binance.client import Client
import time
from datetime import datetime
import os

# Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
START_DATE = "1 Jan 2023"
END_DATE = "1 Jan 2025"
DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

client = Client() # Public access

def download_data(symbol):
    print(f"Downloading {symbol}...")
    klines = client.get_historical_klines(
        symbol, 
        INTERVAL, 
        START_DATE, 
        END_DATE
    )
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df.to_csv(f"{DATA_DIR}/{symbol}.csv")
    print(f"Saved {symbol} to {DATA_DIR}/{symbol}.csv")

for symbol in SYMBOLS:
    download_data(symbol)
