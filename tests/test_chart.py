from services.bybit_service import Bybit
from services.discord_service import send_discord_image

import pandas as pd
from core.chart import generate_trade_chart

Bybit = Bybit()
session = Bybit.session

df = session.klines('BTCUSDT', 1)
df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
df.set_index('time', inplace=True)

print("Testing chart generation...")
img = generate_trade_chart(df, 'BTCUSDT', 'buy', 80500, 79500, 81000)
send_discord_image('TEST CHART BTCUSDT BUY', img)