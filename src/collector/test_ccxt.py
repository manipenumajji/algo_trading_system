import ccxt
import pandas as pd
exchange=ccxt.binance()
data=exchange.fetch_ohlcv("BTC/USDT","1h",limit=5)
print(pd.to_datetime(data[0][0],unit="ms"))