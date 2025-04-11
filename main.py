import time
import pandas as pd
from services.bybit_service import Bybit
from services.discord_service import send_discord, send_discord_image
from core.trailing_stop import update_trailing_stop
from core.chart import generate_trade_chart
from config import MAX_POSITIONS, SYMBOLS, TIMEFRAME, MODE, LEVERAGE
from core.strategy import Strategy

def run_bot(session : Bybit):
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
                    update_trailing_stop(symbol, positions[symbol], session)
                    continue

                strategy = Strategy(session, symbol)
                signal = strategy.generate_signal()

                if signal:
                    side, sl, tp, qty, trailing = signal
                    mark_price = float(session.get_tickers('linear', symbol, 10000)['result']['list'][0]['markPrice'])

                    est_profit = round(abs(tp - mark_price) * qty, 2)
                    est_loss = round(abs(mark_price - sl) * qty, 2)

                    df = session.klines(symbol, TIMEFRAME)
                    df['time'] = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
                    df.set_index('time', inplace=True)

                    msg = (
                        f'{symbol} {mark_price} | {side.upper()} | SL: {sl} | TP: {tp} | '
                        f'QTY: {qty}, TRAILING: {trailing}\n'
                        f'Est. Profit: {est_profit} USDT | Est. Loss: {est_loss} USDT'
                    )

                    img = generate_trade_chart(df, symbol, side, mark_price, sl, tp)
                    print(msg)
                    
                    send_discord_image(msg, img)
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

if __name__ == "__main__":
    session = Bybit()
    print(session.get_balance())
    send_discord(f"Bot started! {session.get_balance()} USDT")
    run_bot(session)