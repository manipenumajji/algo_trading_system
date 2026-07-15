import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

from src.utils.logger import logger
from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)


class DatabaseManager:

    def __init__(self):

        self.connection = None
        self.cursor = None

        self.connect()

    def connect(self):

        try:
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            self.cursor = self.connection.cursor()

            logger.info(
                "Successfully connected to PostgreSQL."
            )

        except Exception as e:
            logger.error(
                f"Failed to connect to database: {e}"
            )
            raise

    def create_tables(self):

        try:

            query = """
            CREATE TABLE IF NOT EXISTS ohlcv (
                symbol VARCHAR(20),
                timeframe VARCHAR(10),
                timestamp TIMESTAMP,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION,

                PRIMARY KEY (
                    symbol,
                    timeframe,
                    timestamp
                )
            );
            """

            self.cursor.execute(query)

            self.connection.commit()

            logger.info(
                "OHLCV table created successfully."
            )

            self.create_labels_table()

        except Exception as e:

            logger.error(
                f"Failed to create table: {e}"
            )

            raise
    def create_labels_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS labels_v1 (
            symbol VARCHAR(20),
            timestamp TIMESTAMP,

            long_label INTEGER,
            short_label INTEGER,

            entry_price DOUBLE PRECISION,

            long_sl DOUBLE PRECISION,
            long_tp DOUBLE PRECISION,

            short_sl DOUBLE PRECISION,
            short_tp DOUBLE PRECISION,

            PRIMARY KEY (
                symbol,
                timestamp
            )
        );
        """

        self.cursor.execute(query)

        self.connection.commit()

        logger.info(
            "Labels table created successfully."
        )    

    def upsert_ohlcv(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ):

        try:

            values = []

            for timestamp, row in df.iterrows():

                values.append(
            (
                symbol,
                timeframe,
                timestamp.to_pydatetime(),
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                float(row["volume"])
            )
            )
                

            query = """
            INSERT INTO ohlcv (
                symbol,
                timeframe,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            )
            VALUES %s

            ON CONFLICT (
                symbol,
                timeframe,
                timestamp
            )

            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            """

            execute_values(
                self.cursor,
                query,
                values
            )

            self.connection.commit()

            logger.info(
                f"Stored {len(values)} candles for "
                f"{symbol} {timeframe}"
            )

        except Exception as e:
            self.connection.rollback()
            logger.error(
                f"Failed to store OHLCV data: {e}"
            )
            raise

    def get_latest_timestamp(
        self,
        symbol: str,
        timeframe: str
    ):

        try:

            query = """
            SELECT MAX(timestamp)
            FROM ohlcv
            WHERE symbol = %s
            AND timeframe = %s;
            """

            self.cursor.execute(
                query,
                (
                    symbol,
                    timeframe
                )
            )

            result = self.cursor.fetchone()

            return result[0]

        except Exception as e:
            logger.error(
                f"Failed to fetch latest timestamp: {e}"
            )
            raise

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str
    ) -> pd.DataFrame:

        try:

            query = """
            SELECT *
            FROM ohlcv
            WHERE symbol = %s
            AND timeframe = %s
            ORDER BY timestamp ASC;
            """

            self.cursor.execute(
                query,
                (
                    symbol,
                    timeframe
                )
            )

            rows = self.cursor.fetchall()

            df = pd.DataFrame(
                rows,
                columns=[
                    "symbol",
                    "timeframe",
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            return df

        except Exception as e:
            logger.error(
                f"Failed to fetch OHLCV data: {e}"
            )
            raise

    def close(self):

        try:

            if self.cursor:
                self.cursor.close()

            if self.connection:
                self.connection.close()

            logger.info(
                "Database connection closed."
            )

        except Exception as e:
            logger.error(
                f"Failed to close database connection: {e}"
            )
            raise
    def create_labels_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS labels_v1 (
            symbol VARCHAR(20),
            timestamp TIMESTAMP,

            long_label INTEGER,
            short_label INTEGER,

            entry_price DOUBLE PRECISION,

            long_sl DOUBLE PRECISION,
            long_tp DOUBLE PRECISION,

            short_sl DOUBLE PRECISION,
            short_tp DOUBLE PRECISION,

            PRIMARY KEY (
                symbol,
                timestamp
            )
        );
        """

        self.cursor.execute(query)
        self.connection.commit()

        logger.info(
            "Labels table created successfully."
        )    