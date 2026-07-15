from src.exchanges.binance_exchange import BinanceExchange
from src.collector.ohlcv_collector import OHLCVCollector
from src.database.database_manager import DatabaseManager
from src.collector.news_collector import NewsCollector
from src.features.sentiment_engine import SentimentEngine
from src.features.feature_engine import FeatureEngine
from src.ml.label_generator import (LabelGenerator)
from src.ml.train import Trainer

from config import (
    SYMBOLS,
    TIMEFRAMES,
    OHLCV_LIMIT,
    NEWS_API_KEY,
    NEWS_ASSETS,
    NEWS_LOOKBACK_HOURS,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
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

    news_collector = NewsCollector(
        api_key=NEWS_API_KEY,
        assets=NEWS_ASSETS,
        db_config={
            "host": DB_HOST,
            "database": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "port": DB_PORT
        },
        hours_back=NEWS_LOOKBACK_HOURS
    )

    news_collector.fetch_all()
    logger.info("News collection completed.")


    sentiment_engine = SentimentEngine(
    db_config={
        "host": DB_HOST,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "port": DB_PORT
    }
)

    sentiment_engine.run()

    logger.info("Sentiment calculation completed.")

    feature_engine = FeatureEngine(
    db_config={
        "host": DB_HOST,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "port": DB_PORT
    }
)

    feature_engine.run()
    
    label_generator = LabelGenerator(
        db_manager
    )

    label_generator.run()

    logger.info(
        "Label generation completed."
    )

    logger.info(
        "Feature generation completed."
    )
    trainer = Trainer(
    db_manager
    )

    trainer.run()

    db_manager.close()


if __name__ == "__main__":
    main()