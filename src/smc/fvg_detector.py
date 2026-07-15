import pandas as pd

from src.utils.logger import logger


class FVGDetector:

    def __init__(
        self,
        atr_multiplier=0.10
    ):
        self.atr_multiplier = atr_multiplier

    def detect(
        self,
        df: pd.DataFrame
    ):

        features = []

        active_bullish_fvgs = []
        active_bearish_fvgs = []

        for i in range(2, len(df)):

            timestamp = df.iloc[i]["timestamp"]

            bullish_fvg_present = 0
            bearish_fvg_present = 0

            fvg_distance_pct = None
            fvg_size_pct = None

            current_high = df.iloc[i]["high"]
            current_low = df.iloc[i]["low"]
            current_close = df.iloc[i]["close"]

            atr = df.iloc[i]["atr_14"]

            # =====================================
            # Bullish FVG
            # =====================================

            bullish_gap = (
                current_low
                -
                df.iloc[i - 2]["high"]
            )

            if (
                current_low >
                df.iloc[i - 2]["high"]
                and
                bullish_gap >=
                (
                    atr *
                    self.atr_multiplier
                )
            ):

                midpoint = (
                    current_low
                    +
                    df.iloc[i - 2]["high"]
                ) / 2

                active_bullish_fvgs.append(
                    {
                        "top": current_low,
                        "bottom":
                        df.iloc[i - 2]["high"],
                        "midpoint":
                        midpoint,
                        "created_at":
                        timestamp
                    }
                )

                bullish_fvg_present = 1

                fvg_distance_pct = (
                    abs(
                        current_close
                        -
                        midpoint
                    )
                    /
                    current_close
                )

                fvg_size_pct = (
                    bullish_gap
                    /
                    current_close
                )

                logger.info(
                    f"Bullish FVG "
                    f"detected "
                    f"bottom="
                    f"{df.iloc[i - 2]['high']} "
                    f"top="
                    f"{current_low}"
                )

            # =====================================
            # Bearish FVG
            # =====================================

            bearish_gap = (
                df.iloc[i - 2]["low"]
                -
                current_high
            )

            if (
                current_high <
                df.iloc[i - 2]["low"]
                and
                bearish_gap >=
                (
                    atr *
                    self.atr_multiplier
                )
            ):

                midpoint = (
                    current_high
                    +
                    df.iloc[i - 2]["low"]
                ) / 2

                active_bearish_fvgs.append(
                    {
                        "top":
                        df.iloc[i - 2]["low"],
                        "bottom":
                        current_high,
                        "midpoint":
                        midpoint,
                        "created_at":
                        timestamp
                    }
                )

                bearish_fvg_present = 1

                fvg_distance_pct = (
                    abs(
                        current_close
                        -
                        midpoint
                    )
                    /
                    current_close
                )

                fvg_size_pct = (
                    bearish_gap
                    /
                    current_close
                )

                logger.info(
                    f"Bearish FVG "
                    f"detected "
                    f"top="
                    f"{df.iloc[i - 2]['low']} "
                    f"bottom="
                    f"{current_high}"
                )

            # =====================================
            # Use nearest active FVG if no
            # new FVG created on this candle
            # =====================================

            if (
                bullish_fvg_present == 0
                and
                bearish_fvg_present == 0
            ):

                nearest_distance = None

                for fvg in (
                    active_bullish_fvgs
                    +
                    active_bearish_fvgs
                ):

                    distance = (
                        abs(
                            current_close
                            -
                            fvg["midpoint"]
                        )
                        /
                        current_close
                    )

                    if (
                        nearest_distance
                        is None
                        or
                        distance <
                        nearest_distance
                    ):

                        nearest_distance = (
                            distance
                        )

                        fvg_distance_pct = (
                            distance
                        )

            features.append(
                {
                    "timestamp":
                    timestamp,

                    "bullish_fvg_present":
                    bullish_fvg_present,

                    "bearish_fvg_present":
                    bearish_fvg_present,

                    "fvg_distance_pct":
                    fvg_distance_pct,

                    "fvg_size_pct":
                    fvg_size_pct
                }
            )

        logger.info(
            f"FVG detection completed."
        )

        return pd.DataFrame(
            features
        )