import pandas as pd
import ta
from config import TIMEFRAME, FAST_MA, SLOW_MA, TREND_MA, ATR_LENGTH, ATR_MULT_BASE, RR, RISK_PERCENT, VOL_MA, TRAILING_ATR_MULT

class Strategy:
    def __init__(self, session, symbol):
        self.session = session
        self.symbol = symbol

    def generate_signal(self):
        df = self.session.klines(self.symbol, TIMEFRAME)
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
        balance = self.session.get_balance()
        risk_per_trade = balance * RISK_PERCENT / 100
        entry = c.Close

        if p.EMA_FAST < p.EMA_SLOW and c.EMA_FAST > c.EMA_SLOW and c.Close > c.EMA_TREND:
            sl = entry - c.ATR * atr_mult
            tp = entry + (entry - sl) * RR
            side = 'buy'
        elif p.EMA_FAST > p.EMA_SLOW and c.EMA_FAST < c.EMA_SLOW and c.Close < c.EMA_TREND:
            sl = entry + c.ATR * atr_mult
            tp = entry - (sl - entry) * RR
            side = 'sell'
        else:
            return None

        risk_per_unit = abs(entry - sl)
        qty = risk_per_trade / risk_per_unit
        trailing = c.ATR * TRAILING_ATR_MULT

        return side, sl, tp, qty, trailing
