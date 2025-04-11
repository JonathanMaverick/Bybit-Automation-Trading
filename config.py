import os
from dotenv import load_dotenv

load_dotenv()

# Bybit API
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE")

# Trading Settings
SYMBOLS = ['BTCUSDT', 'ETHUSDT']
TIMEFRAME = 1
MODE = 1
LEVERAGE = 20
RISK_PERCENT = 1.0
ATR_LENGTH = 14
ATR_MULT_BASE = 1.0
RR = 2.0
FAST_MA = 7
SLOW_MA = 20
TREND_MA = 50
VOL_MA = 20
MAX_POSITIONS = 50 
TRAILING_ATR_MULT = 1.5 

# Discord Webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")