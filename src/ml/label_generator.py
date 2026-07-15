import pandas as pd


class LabelGenerator:

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def load_features(
        self,
        symbol
    ):

        query = """
        SELECT
            timestamp,
            atr_14
        FROM features_v1
        WHERE symbol = %s
        ORDER BY timestamp ASC
        """

        df = pd.read_sql(
            query,
            self.db_manager.connection,
            params=[symbol]
        )

        return df

    def load_prices(
        self,
        symbol
    ):

        query = """
        SELECT
            timestamp,
            high,
            low,
            close
        FROM ohlcv
        WHERE symbol = %s
        AND timeframe = '15m'
        ORDER BY timestamp ASC
        """

        df = pd.read_sql(
            query,
            self.db_manager.connection,
            params=[symbol]
        )

        return df

    def generate_labels(
        self,
        symbol
    ):

        prices = self.load_prices(
            symbol
        )

        features = self.load_features(
            symbol
        )

        df = prices.merge(
            features,
            on="timestamp"
        )

        labels = []

        lookahead = 16

        for i in range(
            len(df) - lookahead
        ):

            entry = df.iloc[i]["close"]

            atr = df.iloc[i]["atr_14"]

            if pd.isna(atr):
                continue

            risk = atr * 1.5

            long_sl = (
                entry - risk
            )

            long_tp = (
                entry + (risk * 2)
            )

            short_sl = (
                entry + risk
            )

            short_tp = (
                entry - (risk * 2)
            )

            long_label = -1
            short_label = -1

            future = df.iloc[
                i + 1:i + lookahead + 1
            ]

            # LONG LABEL
            for _, candle in future.iterrows():

                if candle["low"] <= long_sl:
                    long_label = 0
                    break

                if candle["high"] >= long_tp:
                    long_label = 1
                    break

            # SHORT LABEL
            for _, candle in future.iterrows():

                if candle["high"] >= short_sl:
                    short_label = 0
                    break

                if candle["low"] <= short_tp:
                    short_label = 1
                    break

            labels.append(
        (
            symbol,
            df.iloc[i]["timestamp"],

            int(long_label),
            int(short_label),

            float(entry),

            float(long_sl),
            float(long_tp),

            float(short_sl),
            float(short_tp)
        )
    )

        return labels

    def save_labels(
        self,
        labels
    ):

        cursor = (
            self.db_manager.connection
            .cursor()
        )

        query = """
        INSERT INTO labels_v1 (
            symbol,
            timestamp,

            long_label,
            short_label,

            entry_price,

            long_sl,
            long_tp,

            short_sl,
            short_tp
        )
        VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s
        )
        ON CONFLICT (
            symbol,
            timestamp
        )
        DO NOTHING
        """

        cursor.executemany(
            query,
            labels
        )

        self.db_manager.connection.commit()

        cursor.close()

    def run(self):

        symbols = [
            "BTC/USDT",
            "XRP/USDT",
            "ADA/USDT"
        ]

        for symbol in symbols:

            print(
                f"\nGenerating labels for "
                f"{symbol}"
            )

            labels = self.generate_labels(
                symbol
            )

            self.save_labels(
                labels
            )

            print(
                f"Stored "
                f"{len(labels)} labels "
                f"for {symbol}"
            )