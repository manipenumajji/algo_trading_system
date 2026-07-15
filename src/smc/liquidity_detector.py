import pandas as pd

from src.utils.logger import logger


class LiquidityDetector:

    def __init__(
        self,
        threshold_pct=0.001
    ):
        self.threshold_pct = threshold_pct

    def detect(
        self,
        df: pd.DataFrame,
        swings: pd.DataFrame
    ):

        results = []

        swing_highs = []
        swing_lows = []

        equal_high_count = 0
        equal_low_count = 0
        sweep_count = 0

        swing_map = {}

        for _, row in swings.iterrows():

            swing_map[
                row["timestamp"]
            ] = row

        for _, candle in df.iterrows():

            timestamp = candle["timestamp"]

            current_high = candle["high"]
            current_low = candle["low"]
            current_close = candle["close"]

            equal_high_present = 0
            equal_low_present = 0

            bullish_sweep = 0
            bearish_sweep = 0

            nearest_equal_high_distance = None
            nearest_equal_low_distance = None

            # ==========================
            # Store swings
            # ==========================

            if timestamp in swing_map:

                swing = swing_map[
                    timestamp
                ]

                if swing["type"] == "high":

                    swing_highs.append(
                        swing["price"]
                    )

                elif swing["type"] == "low":

                    swing_lows.append(
                        swing["price"]
                    )

            # ==========================
            # Equal High Detection
            # ==========================

            for level in swing_highs:

                distance = abs(
                    current_high
                    -
                    level
                ) / level

                if (
                    distance
                    <=
                    self.threshold_pct
                ):

                    equal_high_present = 1
                    equal_high_count += 1

                    nearest_equal_high_distance = (
                        distance
                    )

                    logger.info(
                        f"Equal High "
                        f"detected "
                        f"near {level}"
                    )

                    break

            # ==========================
            # Equal Low Detection
            # ==========================

            for level in swing_lows:

                distance = abs(
                    current_low
                    -
                    level
                ) / level

                if (
                    distance
                    <=
                    self.threshold_pct
                ):

                    equal_low_present = 1
                    equal_low_count += 1

                    nearest_equal_low_distance = (
                        distance
                    )

                    logger.info(
                        f"Equal Low "
                        f"detected "
                        f"near {level}"
                    )

                    break

            # ==========================
            # Liquidity Sweep High
            # ==========================

            for level in swing_highs:

                if (
                    current_high > level
                    and
                    current_close < level
                ):

                    bullish_sweep = 1
                    sweep_count += 1

                    logger.info(
                        f"Buy-side liquidity "
                        f"swept at "
                        f"{level}"
                    )

                    break

            # ==========================
            # Liquidity Sweep Low
            # ==========================

            for level in swing_lows:

                if (
                    current_low < level
                    and
                    current_close > level
                ):

                    bearish_sweep = 1
                    sweep_count += 1

                    logger.info(
                        f"Sell-side liquidity "
                        f"swept at "
                        f"{level}"
                    )

                    break

            results.append(
                {
                    "timestamp":
                    timestamp,

                    "equal_high_present":
                    equal_high_present,

                    "equal_low_present":
                    equal_low_present,

                    "equal_high_count":
                    equal_high_count,

                    "equal_low_count":
                    equal_low_count,

                    "bullish_sweep":
                    bullish_sweep,

                    "bearish_sweep":
                    bearish_sweep,

                    "sweep_count":
                    sweep_count,

                    "equal_high_distance":
                    nearest_equal_high_distance,

                    "equal_low_distance":
                    nearest_equal_low_distance
                }
            )

        logger.info(
            "Liquidity detection completed."
        )

        return pd.DataFrame(
            results
        )