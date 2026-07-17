import pandas as pd
from collections import defaultdict

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

        swing_map = defaultdict(list)

        invalid_structure_logged = False

        for _, swing in swings.iterrows():

            swing_map[
                swing["timestamp"]
            ].append(swing)

        for _, candle in df.iterrows():

            timestamp = candle["timestamp"]
            close_price = candle["close"]

            premium_zone = 0
            discount_zone = 0
            equilibrium_zone = 0

            pd_position = None
            equilibrium_price = None

            # =====================================
            # Update latest swings
            # =====================================

            if timestamp in swing_map:

                for swing in swing_map[timestamp]:

                    if swing["type"] == "high":
                        current_swing_high = (
                            swing["price"]
                        )

                    elif swing["type"] == "low":
                        current_swing_low = (
                            swing["price"]
                        )

            # =====================================
            # Validation
            # =====================================

            if (
                current_swing_high is not None
                and
                current_swing_low is not None
            ):

                if (
                    current_swing_high <=
                    current_swing_low
                ):

                    if not invalid_structure_logged:

                        logger.warning(
                            f"Invalid premium/discount "
                            f"range at {timestamp}: "
                            f"high={current_swing_high}, "
                            f"low={current_swing_low}"
                        )

                        invalid_structure_logged = True

                else:

                    invalid_structure_logged = False

            # =====================================
            # Cannot calculate zones
            # =====================================

            if (
                current_swing_high is None
                or
                current_swing_low is None
                or
                current_swing_high <= current_swing_low
            ):

                results.append(
                    {
                        "timestamp":
                        timestamp,

                        "premium_zone":
                        0,

                        "discount_zone":
                        0,

                        "equilibrium_zone":
                        0,

                        "pd_position":
                        None,

                        "equilibrium_price":
                        None,

                        "range_high":
                        None,

                        "range_low":
                        None
                    }
                )

                continue

            # =====================================
            # Midpoint
            # =====================================

            equilibrium_price = (
                current_swing_high
                +
                current_swing_low
            ) / 2

            # =====================================
            # Position in range
            # =====================================

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

            # =====================================
            # Classification
            # =====================================

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
            "Premium/Discount detection completed."
        )

        return pd.DataFrame(
            results
        )