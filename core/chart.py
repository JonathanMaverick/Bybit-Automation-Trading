import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import io


def generate_trade_chart(df, symbol, side, entry, sl, tp):
    
    color_profit = 'green'
    color_loss = 'red'

    apds = [
        mpf.make_addplot(np.full(len(df), entry), color='yellow', linestyle='--', width=1.2),
        mpf.make_addplot(np.full(len(df), sl), color=color_loss, linestyle='--', width=1.2),
        mpf.make_addplot(np.full(len(df), tp), color=color_profit, linestyle='--', width=1.2),
    ]

    mc = mpf.make_marketcolors(
        up='lime', down='red',
        wick={'up': 'white', 'down': 'white'},
        edge={'up': 'lime', 'down': 'red'},
        volume='in'
    )

    s = mpf.make_mpf_style(
        marketcolors=mc,
        base_mpf_style='nightclouds',
        figcolor='#121212',
        facecolor='#121212',
        gridstyle=':',
        gridcolor='gray',
        rc={'font.size': 8}
    )

    fig, _ = mpf.plot(
        df,
        type='candle',
        style=s,
        addplot=apds,
        returnfig=True,
        volume=True,
        title=f'{symbol} - {side.upper()}',
        ylabel='Price',
        ylabel_lower='Volume',
    )

    ax = fig.axes[0]
    ax.axhspan(min(entry, tp), max(entry, tp), facecolor=color_profit, alpha=0.05)
    ax.axhspan(min(entry, sl), max(entry, sl), facecolor=color_loss, alpha=0.05)

    ax.set_facecolor('#121212')
    fig.set_facecolor('#121212')

    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
    img_buf.seek(0)
    plt.close(fig)

    return img_buf