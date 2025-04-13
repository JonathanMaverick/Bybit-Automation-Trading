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
ATR_MULT_BASE = 1.2  # Lower to reduce stop-loss hits on fast moves
RR = 1.5 # Slightly lower for quicker trades
FAST_MA = 5  # Faster MA for quicker reaction
SLOW_MA = 21  # Standard slower MA
TREND_MA = 55  # Slightly lower trend filter
MAJOR_TREND_MA = 80  # Faster reaction to major trend changes
VOL_MA = 10  # Slightly higher volume filter to avoid too much noise
MAX_POSITIONS = 3  # Keep max positions as is
TRAILING_ATR_MULT = 1.8  # Tighter trailing stop to capture fast moves
TIME_THRESHOLD = 1744113206696  # Ensure correct timestamp, or remove if unnecessary
USE_MAJOR_TREND = True  # Keep major trend filter

# Discord Webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")