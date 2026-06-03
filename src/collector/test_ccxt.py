import ccxt
import pandas as pd
import os
exchange=ccxt.binance()
data=exchange.fetch_ohlcv("BTC/USDT","1h",limit=5)
columns=["timestamp","open","high","low","close","volume"]
dataframe=pd.DataFrame(data,columns=columns)
dataframe["timestamp"]= pd.to_datetime(dataframe["timestamp"],unit="ms")
dataframe.to_csv("data/raw/BTC_USDT_1h.csv",index=False)
print(dataframe)
