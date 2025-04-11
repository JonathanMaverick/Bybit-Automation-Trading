import os
import time
import pandas as pd
import ta
import requests
from dotenv import load_dotenv
from helper import Bybit

# Load ENV
load_dotenv()

# Discord Webhook
discord_webhook = os.getenv('DISCORD_WEBHOOK')

# API Setup
session = Bybit(
    api=os.getenv('API_KEY'),
    secret=os.getenv('SECRET_KEY'),
    accountType=os.getenv('ACCOUNT_TYPE')
)

# Config
SYMBOLS = ['BTCUSDT', 'ETHUSDT']
TIMEFRAME = 1  # 1m
RISK_PERCENT = 2
ATR_LENGTH = 14
ATR_MULT_BASE = 1.0
RR = 2.0
FAST_MA = 7
SLOW_MA = 20
TREND_MA = 50
VOL_MA = 20
MODE = 1
LEVERAGE = 10
MAX_POSITIONS = 200
TRAILING_ATR_MULT = 1.5  # Trailing Stop multiplier

def send_discord(msg):
    requests.post(discord_webhook, json={"content": msg})

def get_signal(symbol):
    df = session.klines(symbol, TIMEFRAME)
    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df.set_index('time', inplace=True)

    if len(df) < SLOW_MA + 10:
        return None

    df['EMA_FAST'] = ta.trend.ema_indicator(df['Close'], FAST_MA)
    df['EMA_SLOW'] = ta.trend.ema_indicator(df['Close'], SLOW_MA)
    df['EMA_TREND'] = ta.trend.ema_indicator(df['Close'], TREND_MA)
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], ATR_LENGTH)
    df['VOL_MA'] = df['Volume'].rolling(VOL_MA).mean()

    c, p = df.iloc[-1], df.iloc[-2]

    if c.Volume < c.VOL_MA:
        return None

    atr_mult = ATR_MULT_BASE + (c.ATR / c.Close) * 8
    balance = session.get_balance()
    risk_per_trade = balance * RISK_PERCENT / 100

    if p.EMA_FAST < p.EMA_SLOW and c.EMA_FAST > c.EMA_SLOW and c.Close > c.EMA_TREND:
        stop = c.Close - c.ATR * atr_mult
        tp = c.Close + (c.Close - stop) * RR
        side = 'buy'
    elif p.EMA_FAST > p.EMA_SLOW and c.EMA_FAST < c.EMA_SLOW and c.Close < c.EMA_TREND:
        stop = c.Close + c.ATR * atr_mult
        tp = c.Close - (stop - c.Close) * RR
        side = 'sell'
    else:
        return None

    risk_per_unit = abs(c.Close - stop)
    qty = risk_per_trade / risk_per_unit
    trailing_distance = c.ATR * TRAILING_ATR_MULT

    return side, stop, tp, qty, trailing_distance


def update_trailing_stop(symbol, position):
    df = session.klines(symbol, TIMEFRAME)
    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df.set_index('time', inplace=True)

    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], ATR_LENGTH)
    c = df.iloc[-1]

    atr_mult = ATR_MULT_BASE + (c.ATR / c.Close) * 8
    entry = float(position['entryPrice'])
    sl = float(position['stopLoss'])
    side = position['side']

    if side == 'Buy':
        new_sl = max(sl, c.Close - c.ATR * atr_mult)
    else:
        new_sl = min(sl, c.Close + c.ATR * atr_mult)

    if new_sl != sl:
        session.edit_position_stop_loss(symbol, new_sl)
        print(f'Updated Trailing SL {symbol} {side.upper()}: {new_sl}')

send_discord(f"Bot started! {session.get_balance()} USDT")

while True:
    try:
        balance = session.get_balance()
        print(f'Balance: {round(balance, 3)} USDT')

        positions = session.get_positions()
        print(f'{len(positions)} Active Positions: {positions}')

        if len(positions) >= MAX_POSITIONS:
            print("Max positions reached!")
            time.sleep(60)
            continue

        for symbol in SYMBOLS:
            if symbol in positions:
                update_trailing_stop(symbol, positions[symbol])
                continue

            signal = get_signal(symbol)
            if signal:
                side, sl, tp, qty, trailing = signal
                mark_price = float(session.get_tickers(
                    category='linear',
                    symbol=symbol,
                    recv_window=10000
                )['result']['list'][0]['markPrice'])
                msg = f'{symbol} {mark_price} | {side.upper()} | SL: {sl} | TP: {tp} | QTY: {qty}, TRAILING: {trailing}'
                print(msg)
                send_discord(msg)
                session.place_order_market(symbol, side, MODE, LEVERAGE, qty, tp, sl, trailing)
                time.sleep(1)

        now = int(time.time())
        wait = (TIMEFRAME * 60) - (now % (TIMEFRAME * 60))
        print(f'Waiting {wait}s for next candle...')
        time.sleep(wait)

    except Exception as e:
        print(f'Error: {e}')
        time.sleep(30)
