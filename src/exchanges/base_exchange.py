from abc import ABC, abstractmethod
import pandas as pd
class BaseExchange(ABC):
    @abstractmethod
    def fetch_ohlcv(self,symbol:str,timeframe:str,limit: int=1000,since=None)->pd.DataFrame:# fetches market data
        pass
    @abstractmethod
    def fetch_balance(self) ->dict: # To see the balance in the exchange 
        pass
    @abstractmethod
    def place_order(self,symbol:str,side:str,amount:float,order_type:str="market",price:dict |None=None): # To place a trade we use this function
        pass
    @abstractmethod
    def fetch_positions(self)->list: # To see the trades which are actually active
        pass
    @abstractmethod
    def cancel_order(self,order_id:bool): # to cancle the trade 
        pass