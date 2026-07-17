import pandas as pd

from src.smc.swing_detector import SwingDetector
from src.smc.bos_choch_detector import BOSCHOCHDetector

from src.utils.logger import logger


class HigherTFBias:
    """
    Calculates directional market bias using
    higher timeframe market structure.

    Trend comes directly from BOS/CHOCH detection:
        1  -> bullish
        0  -> neutral
       -1  -> bearish
    """

    def __init__(
        self,
        swing_atr_multiplier: float = 1.5
    ):

        self.swing_detector = SwingDetector(
            atr_multiplier=swing_atr_multiplier
        )

        self.bos_detector = BOSCHOCHDetector()

    def calculate(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        logger.info(
            "Calculating higher timeframe bias..."
        )

        swings = (
            self.swing_detector
            .detect_swings(df)
        )

        bos_features = (
            self.bos_detector
            .detect(
                df,
                swings
            )
        )

        if (
            bos_features.empty
            or
            "trend" not in bos_features.columns
        ):

            logger.warning(
                "Higher timeframe bias "
                "could not be calculated."
            )

            return pd.DataFrame(
                {
                    "timestamp":
                    df["timestamp"],

                    "bias":
                    "neutral",

                    "bias_value":
                    0
                }
            )

        bias_value = (
            bos_features["trend"]
            .fillna(0)
            .astype(int)
        )

        bias = bias_value.map(
            lambda x:
            "bullish"
            if x == 1
            else (
                "bearish"
                if x == -1
                else "neutral"
            )
        )

        result = pd.DataFrame(
            {
                "timestamp":
                bos_features["timestamp"],

                "bias":
                bias,

                "bias_value":
                bias_value
            }
        )

        logger.info(
            f"Higher timeframe bias "
            f"calculated for "
            f"{len(result)} candles."
        )

        return result