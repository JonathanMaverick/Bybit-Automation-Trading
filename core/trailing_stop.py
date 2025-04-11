from config import LEVERAGE, MODE
from services.discord_service import send_discord

def update_trailing_stop(symbol, position, session):
    if not position:
        return
        
    side = position['side'].lower()
    entry = float(position['entryPrice'])
    mark_price = float(session.get_tickers('linear', symbol, 10000)['result']['list'][0]['markPrice'])
    trailing_stop = float(position['trailingStop'])

    if trailing_stop <= 0:
        return 

    if side == 'buy':
        if mark_price - trailing_stop > entry:
            msg = (
                f"[TRAILING] Updating trailing stop for SHORT {symbol} | "
                f"Entry: {entry} | Mark Price: {mark_price} | Trailing Stop: {trailing_stop}"
            )
            print(msg)
            send_discord(msg)
            session.set_trailing_stop(symbol, position.side, LEVERAGE, position.side)
    elif side == 'sell':
        if trailing_stop - mark_price > entry:
            msg = (
                f"[TRAILING] Updating trailing stop for SHORT {symbol} | "
                f"Entry: {entry} | Mark Price: {mark_price} | Trailing Stop: {trailing_stop}"
            )
            print(msg)
            send_discord(msg)
            session.set_trailing_stop(symbol, MODE, LEVERAGE, position.side)
        return
