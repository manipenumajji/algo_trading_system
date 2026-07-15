import pandas as pd

from src.utils.logger import logger


class BOSCHOCHDetector:

    def __init__(self):
        pass

    def detect(
        self,
        df: pd.DataFrame,
        swings: pd.DataFrame
    ):

        features = []

        current_trend = 0
        bos_count = 0

        latest_swing_high = None
        latest_swing_low = None

        swing_map = {}

        for _, swing in swings.iterrows():

            swing_map[
                swing["timestamp"]
            ] = swing

        for _, row in df.iterrows():

            timestamp = row["timestamp"]
            close_price = row["close"]

            bullish_bos = 0
            bearish_bos = 0

            bullish_choch = 0
            bearish_choch = 0

            if timestamp in swing_map:

                swing = swing_map[timestamp]

                if swing["type"] == "high":
                    latest_swing_high = (
                        swing["price"]
                    )

                elif swing["type"] == "low":
                    latest_swing_low = (
                        swing["price"]
                    )

            # -------------------------
            # Bullish BOS
            # -------------------------

            if (
                latest_swing_high is not None
                and
                close_price >
                latest_swing_high
            ):

                bullish_bos = 1
                bos_count += 1

                logger.info(
                    f"Bullish BOS detected "
                    f"close={close_price} "
                    f"break={latest_swing_high}"
                )

                if current_trend == -1:

                    bullish_choch = 1

                    logger.info(
                        f"Bullish CHOCH "
                        f"detected "
                        f"close={close_price}"
                    )

                current_trend = 1

            # -------------------------
            # Bearish BOS
            # -------------------------

            elif (
                latest_swing_low is not None
                and
                close_price <
                latest_swing_low
            ):

                bearish_bos = 1
                bos_count += 1

                logger.info(
                    f"Bearish BOS detected "
                    f"close={close_price} "
                    f"break={latest_swing_low}"
                )

                if current_trend == 1:

                    bearish_choch = 1

                    logger.info(
                        f"Bearish CHOCH "
                        f"detected "
                        f"close={close_price}"
                    )

                current_trend = -1

            features.append(
                {
                    "timestamp":
                    timestamp,

                    "bullish_bos":
                    bullish_bos,

                    "bearish_bos":
                    bearish_bos,

                    "bullish_choch":
                    bullish_choch,

                    "bearish_choch":
                    bearish_choch,

                    "bos_count":
                    bos_count,

                    "trend":
                    current_trend,

                    "latest_swing_high":
                    latest_swing_high,

                    "latest_swing_low":
                    latest_swing_low
                }
            )

        logger.info(
            f"BOS/CHOCH detection "
            f"completed."
        )

        return pd.DataFrame(
            features
        )