import pandas as pd

from src.utils.logger import logger


class OrderBlockDetector:

    def __init__(
        self,
        lookback=10
    ):
        self.lookback = lookback

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

            bullish_ob_present = 0
            bearish_ob_present = 0

            bullish_ob_distance = None
            bearish_ob_distance = None

            bullish_ob_high = None
            bullish_ob_low = None

            bearish_ob_high = None
            bearish_ob_low = None

            # ===================================
            # Bullish Order Block
            # ===================================

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

                    # last bearish candle
                    if (
                        candle["close"]
                        <
                        candle["open"]
                    ):

                        bullish_ob_low = (
                            candle["low"]
                        )

                        bullish_ob_high = (
                            candle["high"]
                        )

                        midpoint = (
                            bullish_ob_low
                            +
                            bullish_ob_high
                        ) / 2

                        bullish_obs.append(
                            {
                                "high":
                                bullish_ob_high,

                                "low":
                                bullish_ob_low,

                                "midpoint":
                                midpoint,

                                "created_at":
                                timestamp
                            }
                        )

                        bullish_ob_present = 1

                        logger.info(
                            f"Bullish OB "
                            f"created "
                            f"{bullish_ob_low}"
                            f"-"
                            f"{bullish_ob_high}"
                        )

                        break

            # ===================================
            # Bearish Order Block
            # ===================================

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

                    # last bullish candle
                    if (
                        candle["close"]
                        >
                        candle["open"]
                    ):

                        bearish_ob_low = (
                            candle["low"]
                        )

                        bearish_ob_high = (
                            candle["high"]
                        )

                        midpoint = (
                            bearish_ob_low
                            +
                            bearish_ob_high
                        ) / 2

                        bearish_obs.append(
                            {
                                "high":
                                bearish_ob_high,

                                "low":
                                bearish_ob_low,

                                "midpoint":
                                midpoint,

                                "created_at":
                                timestamp
                            }
                        )

                        bearish_ob_present = 1

                        logger.info(
                            f"Bearish OB "
                            f"created "
                            f"{bearish_ob_low}"
                            f"-"
                            f"{bearish_ob_high}"
                        )

                        break

            # ===================================
            # Distance to nearest bullish OB
            # ===================================

            nearest_distance = None

            for ob in bullish_obs:

                distance = (
                    abs(
                        close_price
                        -
                        ob["midpoint"]
                    )
                    /
                    close_price
                )

                if (
                    nearest_distance
                    is None
                    or
                    distance
                    <
                    nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

            bullish_ob_distance = (
                nearest_distance
            )

            # ===================================
            # Distance to nearest bearish OB
            # ===================================

            nearest_distance = None

            for ob in bearish_obs:

                distance = (
                    abs(
                        close_price
                        -
                        ob["midpoint"]
                    )
                    /
                    close_price
                )

                if (
                    nearest_distance
                    is None
                    or
                    distance
                    <
                    nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

            bearish_ob_distance = (
                nearest_distance
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
            "Order Block detection "
            "completed."
        )

        return pd.DataFrame(
            results
        )