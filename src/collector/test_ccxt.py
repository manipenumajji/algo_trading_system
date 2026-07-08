from abc import ABC, abstractmethod
class BaseExchange(ABC):
    @abstractmethod
    def fetch_ohlcv(self):
        pass
    @abstractmethod
    def get_balance(self):
        pass
class BinanceExchange(BaseExchange):
    pass    
exchange = BinanceExchange()    