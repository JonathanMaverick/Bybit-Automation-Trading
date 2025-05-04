from services.bybit_service import Bybit
from services.discord_service import send_discord_image
from core.chart import generate_trade_chart

import pandas as pd

def test_generate_chart():
    session = Bybit()
    df = session.get_klines('BTCUSDT', 1)
    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df.set_index('time', inplace=True)

    print("Testing chart generation...")
    img = generate_trade_chart(df, 'BTCUSDT', 'buy', 80500, 79500, 81000)
    send_discord_image('TEST CHART BTCUSDT BUY', img)

def test_mark_price():
    session = Bybit()
    mark_price = session.get_mark_price('BTCUSDT')
    print(f"Mark Price: {mark_price}")

def test_balance():
    session = Bybit()
    balance = session.get_balance()
    print(f"Balance: {balance} USDT")
    
def test_get_symbols():
    session = Bybit()
    symbols = session.get_symbols()
    print(f"Symbols: {symbols}")

def test_get_klines():
    session = Bybit()
    df = session.get_klines('BTCUSDT', 1)
    print(f"DataFrame:\n {df}")
    
def test_get_markprice():
    session = Bybit()
    mark_price = session.get_mark_price('BTCUSDT')
    print(f"Mark Price: {mark_price}")

def get_precisions():
    session = Bybit()
    price_precision, qty_precision = session.get_precisions('1000PEPEUSDT')
    print(f"Precision: {price_precision, qty_precision}")

def test_closed_pnl():
    session = Bybit()
    session.check_closed_pnl()

if __name__ == "__main__":
    test_closed_pnl()

