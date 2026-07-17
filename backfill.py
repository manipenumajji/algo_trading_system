import time
from datetime import datetime, timedelta

from src.exchanges.binance_exchange import BinanceExchange
from src.database.database_manager import DatabaseManager

from config import SYMBOLS

from src.utils.logger import logger


# =========================
# Backfill Settings
# =========================

BACKFILL_DAYS = 90          # <-- change this to backfill more/less history

BACKFILL_TIMEFRAMES = [
    "1h",
    "30m",
    "15m",
    "5m"
]

REQUEST_LIMIT = 1000        # candles per API call
REQUEST_DELAY_SECONDS = 0.3 # be polite to the exchange rate limit


TIMEFRAME_MS = {
    "1h": 60 * 60 * 1000,
    "30m": 30 * 60 * 1000,
    "15m": 15 * 60 * 1000,
    "5m": 5 * 60 * 1000,
}


def backfill_symbol_timeframe(
    exchange: BinanceExchange,
    db_manager: DatabaseManager,
    symbol: str,
    timeframe: str,
    start_date: datetime
):

    since = int(start_date.timestamp() * 1000)
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    interval_ms = TIMEFRAME_MS[timeframe]

    total_fetched = 0

    logger.info(
        f"Starting backfill for {symbol} {timeframe} "
        f"from {start_date}"
    )

    while since < now_ms:

        df = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=REQUEST_LIMIT,
            since=since
        )

        if df is None or len(df) == 0:
            logger.info(
                f"No more candles returned for "
                f"{symbol} {timeframe}. Backfill complete."
            )
            break

        db_manager.upsert_ohlcv(
            df=df,
            symbol=symbol,
            timeframe=timeframe
        )

        total_fetched += len(df)

        last_timestamp = df.index[-1]
        since = int(last_timestamp.timestamp() * 1000) + interval_ms

        time.sleep(REQUEST_DELAY_SECONDS)

    logger.info(
        f"Backfill finished for {symbol} {timeframe}: "
        f"{total_fetched} candles stored."
    )


def run_backfill():

    exchange = BinanceExchange()
    db_manager = DatabaseManager()

    db_manager.create_tables()

    start_date = datetime.utcnow() - timedelta(days=BACKFILL_DAYS)

    for symbol in SYMBOLS:

        for timeframe in BACKFILL_TIMEFRAMES:

            try:
                backfill_symbol_timeframe(
                    exchange=exchange,
                    db_manager=db_manager,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date
                )

            except Exception as e:
                logger.error(
                    f"Backfill failed for {symbol} {timeframe}: {e}"
                )

    db_manager.close()

    logger.info("All backfills completed.")


if __name__ == "__main__":
    run_backfill()