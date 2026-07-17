import pandas as pd
import psycopg2

from ta.volatility import AverageTrueRange

from src.smc.market_structure_engine import MarketStructureEngine


class FeatureEngine:

    def __init__(self, db_config):
        self.db_config = db_config
        self.market_structure_engine = MarketStructureEngine()

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def load_data(self, symbol):

        conn = self.get_connection()

        query = """
        SELECT timestamp,
               open,
               high,
               low,
               close,
               volume
        FROM ohlcv
        WHERE symbol = %s
        AND timeframe = '15m'
        ORDER BY timestamp ASC
        """

        df = pd.read_sql(
            query,
            conn,
            params=[symbol]
        )

        conn.close()

        return df

    def load_sentiment(self, symbol):

        asset = symbol.split("/")[0]

        conn = self.get_connection()

        query = """
        SELECT sentiment_score,
               article_count
        FROM news_sentiment
        WHERE asset = %s
        ORDER BY calculated_at DESC
        LIMIT 1
        """

        cursor = conn.cursor()
        cursor.execute(query, (asset,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return row[0], row[1]

        return 0.0, 0

    def get_session(self, hour):

        if 0 <= hour < 8:
            return 0      # Asia

        if 8 <= hour < 13:
            return 1      # London

        if 13 <= hour < 21:
            return 2      # New York

        return 3          # After hours

    def generate_features(self, symbol):

        df = self.load_data(symbol)

        sentiment_score, article_count = (
            self.load_sentiment(symbol)
        )

        df["returns_1h"] = (
            df["close"].pct_change(4)
        )

        df["returns_4h"] = (
            df["close"].pct_change(16)
        )

        df["returns_24h"] = (
            df["close"].pct_change(96)
        )

        atr = AverageTrueRange(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14
        )

        df["atr_14"] = atr.average_true_range()

        df["volatility_20"] = (
            df["close"]
            .pct_change()
            .rolling(20)
            .std()
        )

        df["high_low_range"] = (
            (df["high"] - df["low"])
            / df["close"]
        )

        ema20 = (
            df["close"]
            .ewm(span=20)
            .mean()
        )

        ema50 = (
            df["close"]
            .ewm(span=50)
            .mean()
        )

        df["ema20_distance_pct"] = (
            (df["close"] - ema20)
            / ema20
        )

        df["ema50_distance_pct"] = (
            (df["close"] - ema50)
            / ema50
        )

        df["ema20_above_ema50"] = (
            ema20 > ema50
        )

        volume_ma = (
            df["volume"]
            .rolling(20)
            .mean()
        )

        df["relative_volume"] = (
            df["volume"] / volume_ma
        )

        df["volume_spike"] = (
            df["relative_volume"] > 2
        )

        df["volume_trend"] = (
            df["volume"]
            .pct_change(20)
        )

        df["sentiment_score"] = sentiment_score
        df["article_count"] = article_count

        df["hour_of_day"] = (
            pd.to_datetime(
                df["timestamp"]
            ).dt.hour
        )

        df["day_of_week"] = (
            pd.to_datetime(
                df["timestamp"]
            ).dt.dayofweek
        )

        df["session"] = (
            df["hour_of_day"]
            .apply(self.get_session)
        )

        df = self.market_structure_engine.generate_features(df)

        return df

    def save_features(
        self,
        df,
        symbol
    ):

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO features_v1 (
            symbol,
            timestamp,
            returns_1h,
            returns_4h,
            returns_24h,
            atr_14,
            volatility_20,
            high_low_range,
            ema20_distance_pct,
            ema50_distance_pct,
            ema20_above_ema50,
            relative_volume,
            volume_spike,
            volume_trend,
            sentiment_score,
            article_count,
            hour_of_day,
            day_of_week,
            session
        )
        VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s
        )
        ON CONFLICT(symbol, timestamp)
        DO NOTHING
        """

        inserted = 0

        for _, row in df.iterrows():

            try:

                cursor.execute(
                    query,
                    (
                        symbol,
                        row["timestamp"],

                        row["returns_1h"],
                        row["returns_4h"],
                        row["returns_24h"],

                        row["atr_14"],
                        row["volatility_20"],
                        row["high_low_range"],

                        row["ema20_distance_pct"],
                        row["ema50_distance_pct"],
                        bool(
                            row[
                                "ema20_above_ema50"
                            ]
                        ),

                        row["relative_volume"],
                        bool(
                            row[
                                "volume_spike"
                            ]
                        ),

                        row["volume_trend"],

                        row["sentiment_score"],
                        int(
                            row[
                                "article_count"
                            ]
                        ),

                        int(
                            row[
                                "hour_of_day"
                            ]
                        ),

                        int(
                            row[
                                "day_of_week"
                            ]
                        ),

                        int(
                            row[
                                "session"
                            ]
                        )
                    )
                )

                inserted += 1

            except Exception as e:

                print(
                    f"Failed inserting row "
                    f"{row['timestamp']}: {e}"
                )

                conn.rollback()

        conn.commit()

        print(
            f"Inserted {inserted} feature rows "
            f"for {symbol}"
        )

        conn.close()

    def run(self):

        symbols = [
            "BTC/USDT",
            "XRP/USDT",
            "ADA/USDT"
        ]

        for symbol in symbols:

            print(
                f"\nGenerating features "
                f"for {symbol}"
            )

            df = self.generate_features(
                symbol
            )

            self.save_features(
                df,
                symbol
            )

            print(
                f"Features stored for "
                f"{symbol}"
            )