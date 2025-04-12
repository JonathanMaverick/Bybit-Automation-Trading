import os
from dotenv import load_dotenv

load_dotenv()

# Bybit API
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE")

# Trading Settings
SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    'SOLUSDT',
    'XRPUSDT',
    'DOGEUSDT',
    'ADAUSDT',
    'AVAXUSDT',
    'LINKUSDT',
    'DOTUSDT',
    'ARBUSDT',
    'OPUSDT',
    'ATOMUSDT',
    'APTUSDT',
    'NEARUSDT',
    'INJUSDT',
    'FILUSDT',
    'LTCUSDT',
    'ETCUSDT',
    'APEUSDT',
    'DYDXUSDT',
    'SUIUSDT',
    '1000PEPEUSDT',
    'SEIUSDT',
    'STXUSDT',
    'TIAUSDT',
    '1000FLOKIUSDT',
    'BLURUSDT',
    'GALAUSDT',
    'SANDUSDT',
    'AXSUSDT',
    'GMTUSDT',
    'LDOUSDT',
    'AAVEUSDT',
    'UNIUSDT',
    'CRVUSDT',
    'YFIUSDT',
    'TAOUSDT',
]
TIMEFRAME = 5
MODE = 1
LEVERAGE = 20
RISK_PERCENT = 0.5
ATR_LENGTH = 14
ATR_MULT_BASE = 1.0
RR = 2.0
FAST_MA = 7
SLOW_MA = 20
TREND_MA = 50
VOL_MA = 20
MAX_POSITIONS = 8
TRAILING_ATR_MULT = 1.5 
TIME_THRESHOLD = 1744113206696

# Discord Webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")