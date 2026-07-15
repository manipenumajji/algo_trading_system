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

        for i in range(2, len(df) - 2):

            current_high = df.iloc[i]["high"]
            current_low = df.iloc[i]["low"]

            atr = df.iloc[i]["atr_14"]

            # -------------------------
            # Swing High Detection
            # -------------------------

            is_swing_high = (
                current_high >
                df.iloc[i - 1]["high"]
                and
                current_high >
                df.iloc[i - 2]["high"]
                and
                current_high >
                df.iloc[i + 1]["high"]
                and
                current_high >
                df.iloc[i + 2]["high"]
            )

            if is_swing_high:

                if (
                    previous_swing_high
                    is None
                ):

                    swings.append(
                        {
                            "timestamp":
                            df.iloc[i][
                                "timestamp"
                            ],
                            "price":
                            current_high,
                            "type":
                            "high"
                        }
                    )

                    previous_swing_high = (
                        current_high
                    )

                    logger.info(
                        f"Initial swing "
                        f"high detected "
                        f"{current_high}"
                    )

                else:

                    move_size = (
                        abs(
                            current_high
                            -
                            previous_swing_high
                        )
                    )

                    threshold = (
                        atr *
                        self.atr_multiplier
                    )

                    if (
                        move_size >=
                        threshold
                    ):

                        swings.append(
                            {
                                "timestamp":
                                df.iloc[i][
                                    "timestamp"
                                ],
                                "price":
                                current_high,
                                "type":
                                "high"
                            }
                        )

                        previous_swing_high = (
                            current_high
                        )

                        logger.info(
                            f"Swing high "
                            f"detected "
                            f"price="
                            f"{current_high}"
                            f" "
                            f"move="
                            f"{move_size}"
                            f" "
                            f"threshold="
                            f"{threshold}"
                        )

            # -------------------------
            # Swing Low Detection
            # -------------------------

            is_swing_low = (
                current_low <
                df.iloc[i - 1]["low"]
                and
                current_low <
                df.iloc[i - 2]["low"]
                and
                current_low <
                df.iloc[i + 1]["low"]
                and
                current_low <
                df.iloc[i + 2]["low"]
            )

            if is_swing_low:

                if (
                    previous_swing_low
                    is None
                ):

                    swings.append(
                        {
                            "timestamp":
                            df.iloc[i][
                                "timestamp"
                            ],
                            "price":
                            current_low,
                            "type":
                            "low"
                        }
                    )

                    previous_swing_low = (
                        current_low
                    )

                    logger.info(
                        f"Initial swing "
                        f"low detected "
                        f"{current_low}"
                    )

                else:

                    move_size = (
                        abs(
                            previous_swing_low
                            -
                            current_low
                        )
                    )

                    threshold = (
                        atr *
                        self.atr_multiplier
                    )

                    if (
                        move_size >=
                        threshold
                    ):

                        swings.append(
                            {
                                "timestamp":
                                df.iloc[i][
                                    "timestamp"
                                ],
                                "price":
                                current_low,
                                "type":
                                "low"
                            }
                        )

                        previous_swing_low = (
                            current_low
                        )

                        logger.info(
                            f"Swing low "
                            f"detected "
                            f"price="
                            f"{current_low}"
                            f" "
                            f"move="
                            f"{move_size}"
                            f" "
                            f"threshold="
                            f"{threshold}"
                        )

        logger.info(
            f"Total swings "
            f"detected: "
            f"{len(swings)}"
        )

        return pd.DataFrame(
            swings
        )