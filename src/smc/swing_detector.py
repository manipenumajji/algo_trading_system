import pandas as pd

from src.utils.logger import logger


class SwingDetector:

    def __init__(
        self,
        atr_multiplier=1.5
    ):
        self.atr_multiplier = atr_multiplier

    def detect_swings(
        self,
        df: pd.DataFrame
    ):

        swings = []

        previous_swing_high = None
        previous_swing_low = None

        last_swing_type = None

        for i in range(2, len(df) - 2):

            current_high = df.iloc[i]["high"]
            current_low = df.iloc[i]["low"]

            atr = df.iloc[i]["atr_14"]

            timestamp = df.iloc[i]["timestamp"]

            # ==========================
            # Swing High
            # ==========================

            is_swing_high = (
                current_high > df.iloc[i - 1]["high"]
                and current_high > df.iloc[i - 2]["high"]
                and current_high > df.iloc[i + 1]["high"]
                and current_high > df.iloc[i + 2]["high"]
            )

            if (
                is_swing_high
                and
                last_swing_type != "high"
            ):

                if (
                    previous_swing_high is None
                    or
                    abs(
                        current_high -
                        previous_swing_high
                    ) >= (
                        atr *
                        self.atr_multiplier
                    )
                ):

                    swings.append(
                        {
                            "timestamp": timestamp,
                            "price": current_high,
                            "type": "high"
                        }
                    )

                    previous_swing_high = current_high
                    last_swing_type = "high"

                    logger.debug(
                        f"Swing high detected "
                        f"{current_high}"
                    )

            # ==========================
            # Swing Low
            # ==========================

            is_swing_low = (
                current_low < df.iloc[i - 1]["low"]
                and current_low < df.iloc[i - 2]["low"]
                and current_low < df.iloc[i + 1]["low"]
                and current_low < df.iloc[i + 2]["low"]
            )

            if (
                is_swing_low
                and
                last_swing_type != "low"
            ):

                if (
                    previous_swing_low is None
                    or
                    abs(
                        previous_swing_low -
                        current_low
                    ) >= (
                        atr *
                        self.atr_multiplier
                    )
                ):

                    swings.append(
                        {
                            "timestamp": timestamp,
                            "price": current_low,
                            "type": "low"
                        }
                    )

                    previous_swing_low = current_low
                    last_swing_type = "low"

                    logger.debug(
                        f"Swing low detected "
                        f"{current_low}"
                    )

        logger.info(
            f"Total swings detected: "
            f"{len(swings)}"
        )

        return pd.DataFrame(
            swings
        )