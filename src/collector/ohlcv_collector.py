import pandas as pd
from src.utils.logger import logger
from src.exchanges.base_exchange import BaseExchange
class OHLCVCollector:

    def __init__(
    self,
    exchange: BaseExchange,
    db_manager,
    symbols: list[str],
    timeframes: list[str],
    limit: int = 1000
    ):

        self.exchange = exchange
        self.db_manager = db_manager
        self.symbols = symbols
        self.timeframes = timeframes
        self.limit = limit

    def fetch_single(
    self,
    symbol: str,
    timeframe: str
    ) -> pd.DataFrame:

        try:
            latest_timestamp = self.db_manager.get_latest_timestamp(
                symbol=symbol,
                timeframe=timeframe
            )

            since = None

            if latest_timestamp is not None:
                since = int(
                    latest_timestamp.timestamp() * 1000
                )

            logger.info(
                f"Latest database timestamp for "
                f"{symbol} {timeframe}: {latest_timestamp}"
            )

            logger.info(
                f"Fetching {symbol} {timeframe} candles..."
            )

            df = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=self.limit,
                since=since
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

    def fetch_all(self) -> None:

        for symbol in self.symbols:

            for timeframe in self.timeframes:

                try:
                    df = self.fetch_single(
                        symbol=symbol,
                        timeframe=timeframe
                    )

                    self.db_manager.upsert_ohlcv(
                        df=df,
                        symbol=symbol,
                        timeframe=timeframe
                    )

                except Exception as e:
                    logger.error(
                        f"Pipeline failed for "
                        f"{symbol} {timeframe}: {e}"
                    )