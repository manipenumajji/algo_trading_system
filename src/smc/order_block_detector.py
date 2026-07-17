import pandas as pd

from src.utils.logger import logger


class OrderBlockDetector:

    def __init__(
        self,
        lookback=20,
        displacement_multiplier=1.5
    ):

        self.lookback = lookback

        self.displacement_multiplier = (
            displacement_multiplier
        )

    def detect(
        self,
        df: pd.DataFrame,
        bos_df: pd.DataFrame
    ):

        bullish_obs = []
        bearish_obs = []

        results = []

        bos_map = {}

        for _, row in bos_df.iterrows():

            bos_map[
                row["timestamp"]
            ] = row

        for i in range(
            self.lookback,
            len(df)
        ):

            timestamp = (
                df.iloc[i]["timestamp"]
            )

            close_price = (
                df.iloc[i]["close"]
            )

            # ==================================
            # Remove invalid bullish OBs
            # ==================================

            bullish_obs = [
                ob
                for ob in bullish_obs
                if close_price > ob["low"]
            ]

            # ==================================
            # Remove invalid bearish OBs
            # ==================================

            bearish_obs = [
                ob
                for ob in bearish_obs
                if close_price < ob["high"]
            ]

            # ==================================
            # Create bullish OB
            # ==================================

            if (
                timestamp in bos_map
                and
                bos_map[timestamp][
                    "bullish_bos"
                ] == 1
            ):

                for j in range(
                    i - 1,
                    max(
                        i - self.lookback,
                        0
                    ),
                    -1
                ):

                    candle = df.iloc[j]

                    if (
                        candle["close"]
                        <
                        candle["open"]
                    ):

                        bullish_obs.append(
                            {
                                "high":
                                candle["high"],

                                "low":
                                candle["low"],

                                "midpoint":
                                (
                                    candle["high"]
                                    +
                                    candle["low"]
                                ) / 2,

                                "created_at":
                                timestamp
                            }
                        )

                        logger.debug(
                            f"Bullish OB created "
                            f"{candle['low']}"
                            f"-"
                            f"{candle['high']}"
                        )

                        break

            # ==================================
            # Create bearish OB
            # ==================================

            if (
                timestamp in bos_map
                and
                bos_map[timestamp][
                    "bearish_bos"
                ] == 1
            ):

                for j in range(
                    i - 1,
                    max(
                        i - self.lookback,
                        0
                    ),
                    -1
                ):

                    candle = df.iloc[j]

                    if (
                        candle["close"]
                        >
                        candle["open"]
                    ):

                        bearish_obs.append(
                            {
                                "high":
                                candle["high"],

                                "low":
                                candle["low"],

                                "midpoint":
                                (
                                    candle["high"]
                                    +
                                    candle["low"]
                                ) / 2,

                                "created_at":
                                timestamp
                            }
                        )

                        logger.debug(
                            f"Bearish OB created "
                            f"{candle['low']}"
                            f"-"
                            f"{candle['high']}"
                        )

                        break

            # ==================================
            # Active OB status
            # ==================================

            bullish_ob_present = (
                1
                if len(
                    bullish_obs
                ) > 0
                else 0
            )

            bearish_ob_present = (
                1
                if len(
                    bearish_obs
                ) > 0
                else 0
            )

            bullish_ob_distance = None
            bearish_ob_distance = None

            bullish_ob_high = None
            bullish_ob_low = None

            bearish_ob_high = None
            bearish_ob_low = None

            # nearest bullish OB

            if bullish_obs:

                nearest = min(
                    bullish_obs,
                    key=lambda x:
                    abs(
                        close_price
                        -
                        x["midpoint"]
                    )
                )

                bullish_ob_distance = (
                    abs(
                        close_price
                        -
                        nearest["midpoint"]
                    )
                    /
                    close_price
                )

                bullish_ob_high = (
                    nearest["high"]
                )

                bullish_ob_low = (
                    nearest["low"]
                )

            # nearest bearish OB

            if bearish_obs:

                nearest = min(
                    bearish_obs,
                    key=lambda x:
                    abs(
                        close_price
                        -
                        x["midpoint"]
                    )
                )

                bearish_ob_distance = (
                    abs(
                        close_price
                        -
                        nearest["midpoint"]
                    )
                    /
                    close_price
                )

                bearish_ob_high = (
                    nearest["high"]
                )

                bearish_ob_low = (
                    nearest["low"]
                )

            results.append(
                {
                    "timestamp":
                    timestamp,

                    "bullish_ob_present":
                    bullish_ob_present,

                    "bearish_ob_present":
                    bearish_ob_present,

                    "bullish_ob_distance":
                    bullish_ob_distance,

                    "bearish_ob_distance":
                    bearish_ob_distance,

                    "bullish_ob_high":
                    bullish_ob_high,

                    "bullish_ob_low":
                    bullish_ob_low,

                    "bearish_ob_high":
                    bearish_ob_high,

                    "bearish_ob_low":
                    bearish_ob_low
                }
            )

        logger.info(
            "Order Block detection completed."
        )

        return pd.DataFrame(
            results
        )