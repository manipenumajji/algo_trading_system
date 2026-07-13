from src.exchanges.binance_exchange import BinanceExchange
from src.collector.ohlcv_collector import OHLCVCollector
from src.database.database_manager import DatabaseManager
from src.config.config import (
    SYMBOLS,
    TIMEFRAMES,
    OHLCV_LIMIT
)
from src.utils.logger import logger
def main():

    exchange = BinanceExchange()

    db_manager = DatabaseManager()

    db_manager.create_tables()

    collector = OHLCVCollector(
        exchange=exchange,
        db_manager=db_manager,
        symbols=SYMBOLS,
        timeframes=TIMEFRAMES,
        limit=OHLCV_LIMIT
    )

    collector.fetch_all()
    logger.info("OHLCV collection completed.")

    db_manager.close()
if __name__ == "__main__":
    main()