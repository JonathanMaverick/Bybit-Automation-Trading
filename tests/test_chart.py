from main import session, generate_trade_chart, send_discord_image
import pandas as pd

df = session.klines('BTCUSDT', 1)
df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
df.set_index('time', inplace=True)

print("Testing chart generation...")
img = generate_trade_chart(df, 'BTCUSDT', 'buy', 80500, 79500, 81000)
send_discord_image('TEST CHART BTCUSDT BUY', img)
