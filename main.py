import time
import pandas as pd

from config import MAX_POSITIONS, SYMBOLS, TIMEFRAME, MODE, LEVERAGE
from services.bybit_service import Bybit
from services.discord_service import send_discord, send_discord_image
from core.strategy import Strategy
from core.trailing_stop import update_trailing_stop
from core.chart import generate_trade_chart


def process_signal(session: Bybit, symbol: str):
    strategy = Strategy(session, symbol)
    signal = strategy.generate_signal()
    print(f'Processing {symbol}...')

    if not signal:
        return
    
    send_discord(f'Getting singal for {symbol}...')
    side, sl, tp, qty, trailing = signal
    mark_price = session.get_mark_price(symbol)

    est_profit = round(abs(tp - mark_price) * qty, 2)
    est_loss = round(abs(mark_price - sl) * qty, 2)

    emoji = "🟢" if side == "buy" else "🔴"
    color = "LONG" if side == "buy" else "SHORT"
    
    rr = round(est_profit / est_loss, 2) if est_loss > 0 else 0
    
    price_precision, _ = session.get_precisions(symbol)
    trailing_stop = str(round(float(trailing), price_precision))

    msg = (
        f'{emoji} [{symbol}] {color} SIGNAL {emoji}\n'
        f'Entry: `{mark_price}` | SL: `{sl}` | TP: `{tp}` | RR: `{rr}`\n'
        f'Qty: `{qty}` | Trailing: `{trailing_stop}`\n'
        f'Est. Profit: `{est_profit} USDT` | Est. Loss: `{est_loss} USDT`'
    )

    print(msg)
    
    df = session.get_klines(symbol, TIMEFRAME)
    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df.set_index('time', inplace=True)
    img = generate_trade_chart(df, symbol, side, mark_price, sl, tp)
    send_discord_image(msg, img)

    session.place_market_order(symbol, side, MODE, LEVERAGE, qty, tp, sl, trailing_stop)
    session.set_trailing_stop(symbol, side.title(), LEVERAGE, trailing_stop)
    time.sleep(1)

def run_bot(session: Bybit):
    while True:
        try:
            balance = round(session.get_balance(), 3)
            session.check_closed_pnl()
            print(f'Balance: {balance} USDT')

            positions = session.get_positions()
            print(f'{len(positions)} Active Positions: {positions}')

            if len(positions) >= MAX_POSITIONS:
                print("Max positions reached!")
                for symbol in positions:
                    update_trailing_stop(symbol, session)
            else:
                for symbol in SYMBOLS:
                    if symbol in positions:
                        update_trailing_stop(symbol, session)  
                    else:
                        process_signal(session, symbol)
                        time.sleep(0.05)

            now = int(time.time())
            wait = (TIMEFRAME * 60) - (now % (TIMEFRAME * 60))
            print(f'Waiting {wait}s for next candle...')
            time.sleep(wait)

        except Exception as e:
            print(f'Error: {e}')
            time.sleep(30)


if __name__ == "__main__":
    session = Bybit()
    balance = round(session.get_balance(), 3)
    positions = session.get_positions()
    msg = (
        f'======================\n'
        f'Bot started!\n'
        f'Balance: {balance} USDT\n'
        f'{len(positions)} Active Positions : {positions}\n'
        f'======================'
    )
    send_discord(msg)
    print(msg)
    session.calculate_total_pnl()
    run_bot(session)
