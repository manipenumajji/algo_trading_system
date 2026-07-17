import pandas as pd
from collections import defaultdict

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

        swing_map = defaultdict(list)

        for _, row in swings.iterrows():

            swing_map[
                row["timestamp"]
            ].append(row)

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

            # ==================================
            # Update swings
            # ==================================

            if timestamp in swing_map:

                for swing in swing_map[timestamp]:

                    if swing["type"] == "high":
                        swing_highs.append(
                            swing["price"]
                        )

                    elif swing["type"] == "low":
                        swing_lows.append(
                            swing["price"]
                        )

            # ==================================
            # Equal highs
            # ==================================

            if len(swing_highs) >= 2:

                latest_high = swing_highs[-1]

                for previous_high in swing_highs[:-1]:

                    distance = (
                        abs(
                            latest_high
                            -
                            previous_high
                        )
                        /
                        previous_high
                    )

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

                        logger.debug(
                            f"Equal High formed "
                            f"between "
                            f"{latest_high} "
                            f"and "
                            f"{previous_high}"
                        )

                        break

            # ==================================
            # Equal lows
            # ==================================

            if len(swing_lows) >= 2:

                latest_low = swing_lows[-1]

                for previous_low in swing_lows[:-1]:

                    distance = (
                        abs(
                            latest_low
                            -
                            previous_low
                        )
                        /
                        previous_low
                    )

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

                        logger.debug(
                            f"Equal Low formed "
                            f"between "
                            f"{latest_low} "
                            f"and "
                            f"{previous_low}"
                        )

                        break

            # ==================================
            # Buy-side sweep
            # ==================================

            for level in swing_highs:

                if (
                    current_high > level
                    and
                    current_close < level
                ):

                    bullish_sweep = 1
                    sweep_count += 1

                    logger.debug(
                        f"Buy-side liquidity swept "
                        f"at {level}"
                    )

                    break

            # ==================================
            # Sell-side sweep
            # ==================================

            for level in swing_lows:

                if (
                    current_low < level
                    and
                    current_close > level
                ):

                    bearish_sweep = 1
                    sweep_count += 1

                    logger.debug(
                        f"Sell-side liquidity swept "
                        f"at {level}"
                    )

                    break

            results.append(
                {
                    "timestamp": timestamp,
                    "equal_high_present": equal_high_present,
                    "equal_low_present": equal_low_present,
                    "equal_high_count": equal_high_count,
                    "equal_low_count": equal_low_count,
                    "bullish_sweep": bullish_sweep,
                    "bearish_sweep": bearish_sweep,
                    "sweep_count": sweep_count,
                    "equal_high_distance": nearest_equal_high_distance,
                    "equal_low_distance": nearest_equal_low_distance
                }
            )

        logger.info(
            "Liquidity detection completed."
        )

        return pd.DataFrame(results)