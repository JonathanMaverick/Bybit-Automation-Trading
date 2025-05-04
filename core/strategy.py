import pandas as pd
import ta
from config import (
    TIMEFRAME,
    ATR_LENGTH,
    RISK_PERCENT,
    TRAILING_ATR_MULT,
)
from datetime import datetime, time

class Strategy:
    def __init__(self, session, symbol):
        self.session = session
        self.symbol = symbol

    def generate_signal(self):
        now_utc = datetime.utcnow().time()
        if now_utc >= time(0, 0) and now_utc <= time(8, 0):
            return None

        df = self.session.get_klines(self.symbol, TIMEFRAME)
        df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
        df.set_index('time', inplace=True)

        if len(df) < ATR_LENGTH + 10:
            return None

        # Indicators
        atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], ATR_LENGTH).average_true_range()
        df['atr'] = atr
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], 14).rsi()
        df['avg_volume'] = df['volume'].rolling(20).mean()
        df['body'] = (df['close'] - df['open']).abs()
        df['strong_candle'] = df['body'] > (df['atr'] * 1.0)
        df['high_volume'] = df['volume'] > df['avg_volume'] * 1.2

        # Supertrend calculation
        def calculate_supertrend(df, multiplier):
            hl2 = (df['high'] + df['low']) / 2
            atr = df['atr']
            upperband = hl2 + multiplier * atr
            lowerband = hl2 - multiplier * atr
            supertrend = pd.Series(index=df.index, dtype='float64')
            direction = pd.Series(index=df.index, dtype='int')

            for i in range(1, len(df)):
                if df['close'].iloc[i] > upperband.iloc[i - 1]:
                    direction.iloc[i] = 1
                elif df['close'].iloc[i] < lowerband.iloc[i - 1]:
                    direction.iloc[i] = -1
                else:
                    direction.iloc[i] = direction.iloc[i - 1] if i > 1 else 1
                supertrend.iloc[i] = lowerband.iloc[i] if direction.iloc[i] == 1 else upperband.iloc[i]

            return supertrend, direction

        df['supertrend'], df['direction'] = calculate_supertrend(df, 5.5)

        c, p = df.iloc[-1], df.iloc[-2]
        if c.isna().any() or p.isna().any():
            return None

        buy_signal = (
            c['direction'] == 1 and c['strong_candle'] and c['high_volume'] and c['rsi'] < 70
        )
        sell_signal = (
            c['direction'] == -1 and c['strong_candle'] and c['high_volume'] and c['rsi'] > 30
        )

        if buy_signal:
            side = 'buy'
        elif sell_signal:
            side = 'sell'
        else:
            return None

        entry = self.session.get_mark_price(self.symbol)

        atr_mult = 6.0
        sl = entry - c.atr * atr_mult if side == 'buy' else entry + c.atr * atr_mult
        risk = abs(entry - sl)
        tp = entry + risk * 2.0 if side == 'buy' else entry - risk * 2.0

        balance = self.session.get_balance()
        risk_per_trade = balance * RISK_PERCENT / 100
        qty = risk_per_trade / risk
        trailing = c.atr * TRAILING_ATR_MULT

        price_precision, qty_precision = self.session.get_precisions(self.symbol)
        order_qty = round(qty, qty_precision)
        tp = round(tp, price_precision)
        sl = round(sl, price_precision)
        trailing_stop = str(round(trailing, price_precision)) if trailing > 0 else None

        return side, sl, tp, order_qty, trailing_stop
