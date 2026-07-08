import ccxt
import pandas as pd
from src.exchanges.base_exchange import BaseExchange
from src.utils.logger import logger


class BinanceExchange(BaseExchange):

    def __init__(self):
        self.exchange = ccxt.binance({
            "enableRateLimit": True
        })

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500
    ) -> pd.DataFrame:

        try:
            raw_data = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )

            df = pd.DataFrame(
                raw_data,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                unit="ms"
            )

            df.set_index(
                "timestamp",
                inplace=True
            )

            return df

        except Exception as e:
            logger.error(
                f"Failed to fetch OHLCV for {symbol}: {e}"
            )
            raise

    def fetch_balance(self) -> dict:

        try:
            balance = self.exchange.fetch_balance()
            return balance

        except Exception as e:
            logger.error(
                f"Failed to fetch balance: {e}"
            )
            raise

    def fetch_positions(self) -> list:

        try:
            positions = self.exchange.fetch_positions()
            return positions

        except Exception as e:
            logger.error(
                f"Failed to fetch positions: {e}"
            )
            raise

    def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        order_type: str = "market",
        price: float | None = None
    ) -> dict:

        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )

            return order

        except Exception as e:
            logger.error(
                f"Failed to place order for {symbol}: {e}"
            )
            raise

    def cancel_order(
        self,
        order_id: str,
        symbol: str
    ) -> dict:

        try:
            result = self.exchange.cancel_order(
                id=order_id,
                symbol=symbol
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to cancel order {order_id}: {e}"
            )
            raise