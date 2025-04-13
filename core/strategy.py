import pandas as pd
import ta
from ta.momentum import StochasticOscillator
from config import (
    TIMEFRAME,
    FAST_MA,
    SLOW_MA,
    TREND_MA,
    ATR_LENGTH,
    ATR_MULT_BASE,
    RR,
    RISK_PERCENT,
    VOL_MA,
    TRAILING_ATR_MULT,
    MAJOR_TREND_MA,
    USE_MAJOR_TREND,
    )
from datetime import datetime, time

class Strategy:
    def __init__(self, session, symbol):
        self.session = session
        self.symbol = symbol
    
    def get_dynamic_volume_threshold(self, atr_value, close_price):
        atr_ratio = atr_value / close_price

        # Kalau volatilitas tinggi (atr_ratio > 1%), kita lebih fleksibel (turunin threshold)
        if atr_ratio > 0.01:
            return 0.75  # lebih longgar, sinyal tetap diproses meski volume rendah
        elif atr_ratio < 0.005:
            return 0.9   # market tenang, hanya lanjut jika volume cukup besar
        else:
            return 0.8   # default

    def generate_signal(self):
        now_utc = datetime.utcnow().time()
        if now_utc >= time(0, 0) and now_utc <= time(8, 0):
            return None
        
        df = self.session.get_klines(self.symbol, TIMEFRAME)
        df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
        df.set_index('time', inplace=True)
        if len(df) < SLOW_MA + 10:
            return None
        
        df['EMA_FAST'] = ta.trend.ema_indicator(df['close'], FAST_MA)
        df['EMA_SLOW'] = ta.trend.ema_indicator(df['close'], SLOW_MA)
        df['EMA_TREND'] = ta.trend.ema_indicator(df['close'], TREND_MA)
        df['EMA_200'] = ta.trend.ema_indicator(df['close'], MAJOR_TREND_MA)
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], ATR_LENGTH)
        df['VOL_MA'] = df['volume'].rolling(VOL_MA).mean()
        
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
        df['%K'] = stoch.stoch()
        df['%D'] = stoch.stoch_signal()

        c, p = df.iloc[-1], df.iloc[-2]
        
        if c.isna().any() or p.isna().any():
            return None
        
        dynamic_threshold = self.get_dynamic_volume_threshold(c.ATR, c.close)
        if c.volume < c.VOL_MA * dynamic_threshold:
            return None
        
        if(p.EMA_FAST < p.EMA_SLOW and c.EMA_FAST > c.EMA_SLOW and
            c.close > c.EMA_TREND and
            (not USE_MAJOR_TREND or c.close > c.EMA_200) and
            p['%K'] < p['%D'] and c['%K'] > c['%D'] and p['%K'] < 20
        ):
            side = 'buy'
        elif (
            p.EMA_FAST > p.EMA_SLOW and c.EMA_FAST < c.EMA_SLOW and
            c.close < c.EMA_TREND and
            (not USE_MAJOR_TREND or c.close < c.EMA_200) and
            p['%K'] > p['%D'] and c['%K'] < c['%D'] and p['%K'] > 80
        ):
            side = 'sell'
        else:
            return None

        
        entry = self.session.get_mark_price(self.symbol)
        
        raw_mult = ATR_MULT_BASE + (c.ATR / c.close) * 8
        atr_mult = max(0.5, min(2.0, raw_mult))
        
        sl = entry - c.ATR * atr_mult if side == 'buy' else entry + c.ATR * atr_mult
        risk = abs(entry - sl)
        tp = entry + risk * RR if side == 'buy' else entry - risk * RR

        #Risk Management
        balance = self.session.get_balance()
        risk_per_trade = balance * RISK_PERCENT / 100
        qty = risk_per_trade / risk
        trailing = c.ATR * TRAILING_ATR_MULT
        
        price_precision, qty_precision = self.session.get_precisions(self.symbol)
        order_qty = round(qty, qty_precision)
        tp = round(tp, price_precision) if tp else None
        sl = round(sl, price_precision) if sl else None
        trailing_stop = str(round(trailing, price_precision)) if trailing > 0 else None
        
        return side, sl, tp, order_qty, trailing_stop
