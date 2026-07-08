from src.exchanges.binance_exchange import BinanceExchange
from src.collector.ohlcv_collector import OHLCVCollector
from src.config.config import (
    SYMBOLS,
    TIMEFRAMES,
    OHLCV_LIMIT
)
from src.utils.logger import logger
def main():

    logger.info("Starting trading system...")

    exchange = BinanceExchange()

    collector = OHLCVCollector(
        exchange=exchange,
        symbols=SYMBOLS,
        timeframes=TIMEFRAMES,
        limit=OHLCV_LIMIT
    )
    collector.fetch_all()
    logger.info("OHLCV collection completed.")
if __name__ == "__main__":
    main()