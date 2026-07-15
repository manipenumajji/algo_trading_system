import pandas as pd

from src.utils.logger import logger


class PremiumDiscountDetector:

    def __init__(self):
        pass

    def detect(
        self,
        df: pd.DataFrame,
        swings: pd.DataFrame
    ):

        results = []

        current_swing_high = None
        current_swing_low = None

        swing_map = {}

        for _, swing in swings.iterrows():

            swing_map[
                swing["timestamp"]
            ] = swing

        for _, candle in df.iterrows():

            timestamp = candle["timestamp"]
            close_price = candle["close"]

            premium_zone = 0
            discount_zone = 0
            equilibrium_zone = 0

            pd_position = None
            equilibrium_price = None

            # -------------------------
            # Update latest swings
            # -------------------------

            if timestamp in swing_map:

                swing = swing_map[timestamp]

                if swing["type"] == "high":
                    current_swing_high = (
                        swing["price"]
                    )

                elif swing["type"] == "low":
                    current_swing_low = (
                        swing["price"]
                    )

            # Cannot calculate without range
            if (
                current_swing_high is None
                or
                current_swing_low is None
            ):

                results.append(
                    {
                        "timestamp": timestamp,
                        "premium_zone": 0,
                        "discount_zone": 0,
                        "equilibrium_zone": 0,
                        "pd_position": None,
                        "equilibrium_price": None,
                        "range_high": None,
                        "range_low": None
                    }
                )

                continue

            # -------------------------
            # Range midpoint
            # -------------------------

            equilibrium_price = (
                current_swing_high
                +
                current_swing_low
            ) / 2

            # Position inside range
            pd_position = (
                (
                    close_price
                    -
                    current_swing_low
                )
                /
                (
                    current_swing_high
                    -
                    current_swing_low
                )
            )

            # -------------------------
            # Zone Classification
            # -------------------------

            if pd_position < 0.45:
                discount_zone = 1

            elif pd_position > 0.55:
                premium_zone = 1

            else:
                equilibrium_zone = 1

            results.append(
                {
                    "timestamp":
                    timestamp,

                    "premium_zone":
                    premium_zone,

                    "discount_zone":
                    discount_zone,

                    "equilibrium_zone":
                    equilibrium_zone,

                    "pd_position":
                    pd_position,

                    "equilibrium_price":
                    equilibrium_price,

                    "range_high":
                    current_swing_high,

                    "range_low":
                    current_swing_low
                }
            )

        logger.info(
            "Premium/Discount "
            "detection completed."
        )

        return pd.DataFrame(
            results
        )