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
    'SOLUSDT',
    'DOGEUSDT',
    'AVAXUSDT',
    'ARBUSDT',
    'OPUSDT',
    'LINKUSDT',
    '1000PEPEUSDT',
    'APTUSDT',
    'INJUSDT',
    'LDOUSDT',
    'BLURUSDT',
    'ADAUSDT',
    'SUIUSDT',
    'WIFUSDT',   # kalau suka scalping memecoin
    'SEIUSDT',
    'TIAUSDT'
]
TIMEFRAME = 3
MODE = 1
LEVERAGE = 10
RISK_PERCENT = 1
ATR_LENGTH = 14
ATR_MULT_BASE = 0.8
RR = 2
FAST_MA = 9
SLOW_MA = 21
TREND_MA = 50
MAJOR_TREND_MA = 89
VOL_MA = 10
MAX_POSITIONS = 3
TRAILING_ATR_MULT = 1.5
TIME_THRESHOLD = 1744113206696
USE_MAJOR_TREND = True

# Discord Webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")