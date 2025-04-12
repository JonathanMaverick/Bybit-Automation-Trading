from config import LEVERAGE
from services.discord_service import send_discord

def update_trailing_stop(symbol, session):
        
    position_details = session.get_position_details(symbol)
    if not position_details:
        print(f"No position details found for {symbol}")
        return
    side = position_details['side'].lower()
    entry = float(position_details['avgPrice']) 
    mark_price = session.get_mark_price(symbol)
    trailing_stop = float(position_details['trailingStop'])
    mark_price = session.get_mark_price(symbol)

    if trailing_stop <= 0:
        return

    should_update = False

    if side == 'buy' and mark_price - trailing_stop > entry:
        should_update = True
    elif side == 'sell' and entry - (mark_price + trailing_stop) > 0:
        should_update = True

    if should_update:
        msg = (
            f"[TRAILING] Updating trailing stop for {side.upper()} {symbol} | "
            f"Entry: {entry} | Mark Price: {mark_price} | Trailing Stop: {trailing_stop}"
        )
        print(msg)
        send_discord(msg)
        session.set_trailing_stop(symbol, side, trailing_stop)
