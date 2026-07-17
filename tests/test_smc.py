from src.smc.market_structure_engine import (
    MarketStructureEngine
)

from src.database.database_manager import (
    DatabaseManager
)

import pandas as pd

db = DatabaseManager()

query_15m = """
SELECT *
FROM ohlcv
WHERE symbol='BTC/USDT'
AND timeframe='15m'
ORDER BY timestamp
"""

query_1h = """
SELECT *
FROM ohlcv
WHERE symbol='BTC/USDT'
AND timeframe='1h'
ORDER BY timestamp
"""

df_15m = pd.read_sql(
    query_15m,
    db.connection
)

df_1h = pd.read_sql(
    query_1h,
    db.connection
)

engine = MarketStructureEngine()

features = (
    engine.generate_features(
        df_15m,
        df_1h
    )
)

print()

print(
    "Bullish BOS:",
    features["bullish_bos"].sum()
)

print(
    "Bearish BOS:",
    features["bearish_bos"].sum()
)

print(
    "Bullish FVG:",
    features["bullish_fvg_present"].sum()
)

print(
    "Bearish FVG:",
    features["bearish_fvg_present"].sum()
)

print(
    "Bullish OB:",
    features["bullish_ob_present"].sum()
)

print(
    "Bearish OB:",
    features["bearish_ob_present"].sum()
)

print(
    "Bullish Sweep:",
    features["bullish_sweep"].sum()
)

print(
    "Bearish Sweep:",
    features["bearish_sweep"].sum()
)