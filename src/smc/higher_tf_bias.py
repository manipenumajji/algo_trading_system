import pandas as pd

from src.utils.logger import logger


class HigherTFBias:

    def __init__(
        self,
        ema_fast=50,
        ema_slow=200
    ):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow

    def calculate(
        self,
        df: pd.DataFrame
    ):

        df = df.copy()

        # ==================================
        # Moving Averages
        # ==================================

        df["ema_fast"] = (
            df["close"]
            .ewm(
                span=self.ema_fast,
                adjust=False
            )
            .mean()
        )

        df["ema_slow"] = (
            df["close"]
            .ewm(
                span=self.ema_slow,
                adjust=False
            )
            .mean()
        )

        # ==================================
        # Bias Determination
        # ==================================

        bias_list = []

        for _, row in df.iterrows():

            ema_fast = row["ema_fast"]
            ema_slow = row["ema_slow"]
            close = row["close"]

            bias = "neutral"
            bias_value = 0

            # -------------------------
            # Strong Bullish
            # -------------------------

            if (
                close > ema_fast
                and
                ema_fast > ema_slow
            ):
                bias = "bullish"
                bias_value = 1

            # -------------------------
            # Strong Bearish
            # -------------------------

            elif (
                close < ema_fast
                and
                ema_fast < ema_slow
            ):
                bias = "bearish"
                bias_value = -1

            bias_list.append(
                (
                    bias,
                    bias_value
                )
            )

        df["bias"] = [
            x[0]
            for x in bias_list
        ]

        df["bias_value"] = [
            x[1]
            for x in bias_list
        ]

        logger.info(
            f"Higher timeframe bias "
            f"calculated for "
            f"{len(df)} candles"
        )

        return df[
            [
                "timestamp",
                "bias",
                "bias_value",
                "ema_fast",
                "ema_slow"
            ]
        ]