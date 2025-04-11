import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import io
from config import TIMEFRAME
from core.strategy import Strategy

def generate_trade_chart(strategy: Strategy):
    apds = []
    session = strategy.session
    symbol = strategy.symbol
    side = strategy.mode
    entry = strategy.entry
    sl = strategy.sl
    tp = strategy.tp
    
    df = session.klines(symbol, TIMEFRAME)
    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df.set_index('time', inplace=True)

    entry_line = np.full(len(df), entry)
    sl_line = np.full(len(df), sl)

    apds.append(mpf.make_addplot(entry_line, color='blue', linestyle='--', width=1, label='Entry'))
    apds.append(mpf.make_addplot(sl_line, color='red', linestyle='--', width=1, label='Stop Loss'))

    if tp:
        tp_line = np.full(len(df), tp)
        apds.append(mpf.make_addplot(tp_line, color='green', linestyle='--', width=1, label='Take Profit'))

    fig, _ = mpf.plot(
        df,
        type='candle',
        style='charles',
        addplot=apds,
        returnfig=True,
        volume=True,
        title=f'{symbol} - {side.upper()}',
        ylabel='Price',
        ylabel_lower='Volume',
    )

    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close(fig)

    return img_buf