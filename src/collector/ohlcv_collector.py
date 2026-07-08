import os
import pandas as pd
from src.utils.logger import logger
from src.exchanges.base_exchange import BaseExchange
class OHLCVCollector:

    def __init__(
        self,
        exchange: BaseExchange,
        symbols: list[str],
        timeframes: list[str],
        limit: int = 500
    ):

        self.exchange = exchange
        self.symbols = symbols
        self.timeframes = timeframes
        self.limit = limit

    def fetch_single(
        self,
        symbol: str,
        timeframe: str
    ) -> pd.DataFrame:

        try:
            logger.info(
                f"Fetching {symbol} {timeframe} candles..."
            )

            df = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=self.limit
            )

            logger.info(
                f"Fetched {len(df)} candles for "
                f"{symbol} {timeframe}"
            )

            return df

        except Exception as e:
            logger.error(
                f"Collector failed for "
                f"{symbol} {timeframe}: {e}"
            )
            raise

    def save_to_csv(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ) -> None:

        try:
            os.makedirs(
                "data",
                exist_ok=True
            )

            filename = (
                f"data/"
                f"{symbol.replace('/', '_')}"
                f"_{timeframe}.csv"
            )

            df.to_csv(filename)

            logger.info(
                f"Saved data to {filename}"
            )

        except Exception as e:
            logger.error(
                f"Failed to save CSV "
                f"for {symbol} {timeframe}: {e}"
            )
            raise

    def fetch_all(self) -> None:

        for symbol in self.symbols:

            for timeframe in self.timeframes:

                try:
                    df = self.fetch_single(
                        symbol=symbol,
                        timeframe=timeframe
                    )

                    self.save_to_csv(
                        df=df,
                        symbol=symbol,
                        timeframe=timeframe
                    )

                except Exception as e:
                    logger.error(
                        f"Pipeline failed for "
                        f"{symbol} {timeframe}: {e}"
                    )