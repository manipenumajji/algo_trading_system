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

            current_high = df.iloc[i]["high"]
            current_low = df.iloc[i]["low"]
            current_close = df.iloc[i]["close"]

            atr = df.iloc[i]["atr_14"]

            # =====================================
            # Remove filled bullish FVGs
            # =====================================

            active_bullish_fvgs = [
                fvg
                for fvg in active_bullish_fvgs
                if current_low > fvg["bottom"]
            ]

            # =====================================
            # Remove filled bearish FVGs
            # =====================================

            active_bearish_fvgs = [
                fvg
                for fvg in active_bearish_fvgs
                if current_high < fvg["top"]
            ]

            # =====================================
            # Create bullish FVG
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
                bullish_gap >= (
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
                        "bottom": df.iloc[i - 2]["high"],
                        "midpoint": midpoint,
                        "created_at": timestamp
                    }
                )

                logger.debug(
                    f"Bullish FVG detected "
                    f"bottom={df.iloc[i - 2]['high']} "
                    f"top={current_low}"
                )

            # =====================================
            # Create bearish FVG
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
                bearish_gap >= (
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
                        "top": df.iloc[i - 2]["low"],
                        "bottom": current_high,
                        "midpoint": midpoint,
                        "created_at": timestamp
                    }
                )

                logger.debug(
                    f"Bearish FVG detected "
                    f"top={df.iloc[i - 2]['low']} "
                    f"bottom={current_high}"
                )

            # =====================================
            # Active FVG state
            # =====================================

            bullish_fvg_present = (
                1
                if active_bullish_fvgs
                else 0
            )

            bearish_fvg_present = (
                1
                if active_bearish_fvgs
                else 0
            )

            # =====================================
            # Distance to nearest bullish FVG
            # =====================================

            bullish_fvg_distance_pct = None

            if active_bullish_fvgs:

                nearest = min(
                    active_bullish_fvgs,
                    key=lambda x: abs(
                        current_close
                        -
                        x["midpoint"]
                    )
                )

                bullish_fvg_distance_pct = (
                    abs(
                        current_close
                        -
                        nearest["midpoint"]
                    )
                    /
                    current_close
                )

            # =====================================
            # Distance to nearest bearish FVG
            # =====================================

            bearish_fvg_distance_pct = None

            if active_bearish_fvgs:

                nearest = min(
                    active_bearish_fvgs,
                    key=lambda x: abs(
                        current_close
                        -
                        x["midpoint"]
                    )
                )

                bearish_fvg_distance_pct = (
                    abs(
                        current_close
                        -
                        nearest["midpoint"]
                    )
                    /
                    current_close
                )

            # =====================================
            # Size
            # =====================================

            fvg_size_pct = None

            if bullish_fvg_present:
                fvg_size_pct = (
                    (
                        active_bullish_fvgs[-1]["top"]
                        -
                        active_bullish_fvgs[-1]["bottom"]
                    )
                    /
                    current_close
                )

            elif bearish_fvg_present:
                fvg_size_pct = (
                    (
                        active_bearish_fvgs[-1]["top"]
                        -
                        active_bearish_fvgs[-1]["bottom"]
                    )
                    /
                    current_close
                )

            features.append(
                {
                    "timestamp": timestamp,
                    "bullish_fvg_present": bullish_fvg_present,
                    "bearish_fvg_present": bearish_fvg_present,
                    "bullish_fvg_distance_pct": bullish_fvg_distance_pct,
                    "bearish_fvg_distance_pct": bearish_fvg_distance_pct,
                    "fvg_size_pct": fvg_size_pct
                }
            )

        logger.info(
            "FVG detection completed."
        )

        return pd.DataFrame(
            features
        )