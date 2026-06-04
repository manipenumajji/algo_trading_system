import ccxt
class OHLCVcollector:
    def __init__(self):
        self.exchange=ccxt.binance()
collector=OHLCVcollector()
print(type(collector.exchange))        