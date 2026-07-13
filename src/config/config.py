# =========================
# Exchange Configuration
# =========================

EXCHANGE_NAME = "binance"


# =========================
# Market Configuration
# =========================

SYMBOLS = [
    "BTC/USDT",
    "XRP/USDT",
    "ADA/USDT"
]

TIMEFRAMES = [
    "1h",
    "15m",
    "5m"
]

OHLCV_LIMIT = 500


# =========================
# Risk Management
# =========================

RISK_PER_TRADE = 0.01
DAILY_LOSS_LIMIT = 0.05
MAX_DRAWDOWN = 0.10


# =========================
# Data Storage
# =========================

DATA_FOLDER = "data"


# =========================
# Logging
# =========================

LOG_LEVEL = "INFO"


# =========================
# Trading Mode
# =========================

PAPER_TRADING = True


# =========================
# Telegram Alerts
# =========================

ENABLE_TELEGRAM_ALERTS = False

# ==========================
# Database Configuration
# ==========================

DB_HOST = "localhost"

DB_PORT = 5432

DB_NAME = "algo_trading"

DB_USER = "postgres"

DB_PASSWORD = "Mani@0303"