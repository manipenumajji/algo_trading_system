import ccxt
import pandas as pd
class OHLCVcollector:
    def __init__(self):
        self.exchange=ccxt.binance()
    def fetch_ohlcv(self):
        data=self.exchange.fetch_ohlcv("BTC/USDT","1h",100)
        return data
    def create_dataframe(self,data):    
        dataframe=pd.DataFrame(data,cloumns=["timestamp","open","high","low","close","volume"])
        dataframe["timestamp"]=pd.to_datetime(dataframe["timestamp"],unit="ms")
        return dataframe
    def save_to_csv(self,dataframe):    
        self.to_csv("data\raw\BTC_USDT_1h.csv",index=False)
       