import requests
import pandas as pd

def get_ohlcv(symbol, interval, limit):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval,  # '1', '3', '5', '15', '30', '60', '240', 'D', 'W', 'M'
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()['result']['list']
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "turnover"
    ])
    df = df.astype({
        "timestamp": 'int64', "open": 'float', "high": 'float',
        "low": 'float', "close": 'float', "volume": 'float'
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.sort_values('timestamp')
    return df

# Get the data
df = get_ohlcv("ETHUSDT", "5", 1000000)

# Save to Excel
df.to_excel("ETHUSDT_5m_April2025.xlsx", index=False)

print("Data berhasil disimpan ke 'ETHUSDT_3m_April2025.xlsx'")