import pandas as pd
import numpy as np
from datetime import time
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from ta.momentum import StochasticOscillator

# FAST_MA = 21
# SLOW_MA = 34
# TREND_MA = 55
# MAJOR_TREND_MA = 200
# ATR_LENGTH = 14
# ATR_MULT_BASE = 1.2
# TRAILING_ATR_MULT = 1.0
# VOL_MA = 20
# RR = 2
# RISK_PERCENT = 2
# USE_MAJOR_TREND = True

from config import (
    FAST_MA,
    SLOW_MA,
    TREND_MA,
    MAJOR_TREND_MA,
    ATR_LENGTH,
    ATR_MULT_BASE,
    VOL_MA,
    RR,
    RISK_PERCENT,
    USE_MAJOR_TREND,
)

# Load data
df = pd.read_excel('ETHUSDT_3m_April2025.xlsx')  # Kolom: timestamp, open, high, low, close, volume
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Tambah indikator teknikal
df['EMA_FAST'] = EMAIndicator(df['close'], FAST_MA).ema_indicator()
df['EMA_SLOW'] = EMAIndicator(df['close'], SLOW_MA).ema_indicator()
df['EMA_TREND'] = EMAIndicator(df['close'], TREND_MA).ema_indicator()
df['MAJOR_TREND_EMA'] = EMAIndicator(df['close'], MAJOR_TREND_MA).ema_indicator()
df['ATR'] = AverageTrueRange(df['high'], df['low'], df['close'], ATR_LENGTH).average_true_range()
df['VOL_MA'] = df['volume'].rolling(VOL_MA).mean()

stoch = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
df['%K'] = stoch.stoch()
df['%D'] = stoch.stoch_signal()

# Hitung breakout levels hanya sekali, di luar loop
df['20High'] = df['high'].rolling(20).max()
df['20Low'] = df['low'].rolling(20).min()

# Inisialisasi backtest
initial_balance = 100
balance = initial_balance
positions = []

# Debug counter
count = {"asia_session": 0, "nan": 0, "volume": 0, "crossover": 0, "trend": 0, "major": 0, "stoch": 0, "success": 0, "breakout": 0}

# Loop candle
for i in range(1, len(df)):
    c, p = df.iloc[i], df.iloc[i - 1]
    current_time = c.name.time()

    # Skip Asia session
    if time(1, 0) <= current_time <= time(7, 0):
        count["asia_session"] += 1
        continue

    if c.isna().any() or p.isna().any():
        count["nan"] += 1
        continue

    # Volume filter
    dynamic_threshold = min(1.5, ATR_MULT_BASE + (c.ATR / c.close) * 4)
    volume_cutoff = c.VOL_MA * dynamic_threshold
    if c.volume < volume_cutoff:
        count["volume"] += 1
        continue

    # EMA crossover
    # is_bullish_crossover = p.EMA_FAST < p.EMA_SLOW and c.EMA_FAST > c.EMA_SLOW
    # is_bearish_crossover = p.EMA_FAST > p.EMA_SLOW and c.EMA_FAST < c.EMA_SLOW
    # if not (is_bullish_crossover or is_bearish_crossover):
    #     count["crossover"] += 1
    #     continue
    
    # Trend filter
    in_uptrend = c.close > c.EMA_TREND
    in_downtrend = c.close < c.EMA_TREND
    if not (in_uptrend or in_downtrend):
        count["trend"] += 1
        continue

    # Major trend filter
    pass_major_trend_buy = not USE_MAJOR_TREND or c.close > c.MAJOR_TREND_EMA
    pass_major_trend_sell = not USE_MAJOR_TREND or c.close < c.MAJOR_TREND_EMA
    if not (pass_major_trend_buy or pass_major_trend_sell):
        count["major"] += 1
        continue

    # Stochastic crossover
    stoch_buy = c['%K'] > c['%D'] and p['%K'] < p['%D'] and c['%K'] < 30
    stoch_sell = c['%K'] < c['%D'] and p['%K'] > p['%D'] and c['%K'] > 80
    if not (stoch_buy or stoch_sell):
        count["stoch"] += 1
        continue

    # Breakout condition
    # breakout_buy = c.close > df['20High'].iloc[i-1]
    # breakout_sell = c.close < df['20Low'].iloc[i-1]
        
    # if not (breakout_buy or breakout_sell):
    #     count["breakout"] += 1
    #     continue

    # Jika semua syarat terpenuhi, entry trade
    if in_uptrend and pass_major_trend_buy and stoch_buy :
        side = 'buy'
    # Untuk Sell
    elif in_downtrend and pass_major_trend_sell and stoch_sell:
        side = 'sell'
    else:
        side = None  # Bisa tidak melakukan apa-apa jika tidak ada sinyal jelas
        continue

    count["success"] += 1
    entry = c.close
    raw_mult = ATR_MULT_BASE + (c.ATR / c.close) * 4
    atr_mult = max(0.5, min(2.0, raw_mult))
    sl = entry - c.ATR * atr_mult if side == 'buy' else entry + c.ATR * atr_mult
    risk = abs(entry - sl)
    tp = entry + risk * RR if side == 'buy' else entry - risk * RR

    risk_per_trade = balance * RISK_PERCENT / 100
    qty = risk_per_trade / risk

    # Simulasi outcome
    next_df = df.iloc[i:i+20]
    outcome = None
    for _, r in next_df.iterrows():
        if side == 'buy':
            if r.low <= sl:
                outcome = 'loss'
                balance -= risk_per_trade
                break
            if r.high >= tp:
                outcome = 'win'
                balance += risk_per_trade * RR
                break
        else:
            if r.high >= sl:
                outcome = 'loss'
                balance -= risk_per_trade
                break
            if r.low <= tp:
                outcome = 'win'
                balance += risk_per_trade * RR
                break
    if outcome:
        positions.append({
            'time': c.name, 'side': side, 'entry': entry, 'sl': sl,
            'tp': tp, 'outcome': outcome, 'balance': balance
        })

    
# Hasil akhir
results = pd.DataFrame(positions)
print("\n==== Backtest Summary ====")
print(results)
print("\nOutcome Count:")
print(results['outcome'].value_counts())
print(f"\nFinal Balance: {balance:.2f}, PnL: {balance - initial_balance:.2f}")

# Debug output
print("\n==== Filter Drop Count ====")
for k, v in count.items():
    print(f"{k}: {v}")