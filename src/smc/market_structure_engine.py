import pandas as pd

from src.smc.swing_detector import SwingDetector
from src.smc.bos_choch_detector import BOSCHOCHDetector
from src.smc.fvg_detector import FVGDetector
from src.smc.order_block_detector import OrderBlockDetector
from src.smc.liquidity_detector import LiquidityDetector
from src.smc.premium_discount import PremiumDiscount
from src.smc.higher_tf_bias import HigherTimeframeBias

from src.utils.logger import logger


class MarketStructureEngine:

    def __init__(
        self,
        swing_atr_multiplier=1.5,
        fvg_atr_multiplier=0.1,
        displacement_atr_multiplier=1.5,
        equal_level_threshold=0.001
    ):

        self.swing_detector = SwingDetector(
            atr_multiplier=swing_atr_multiplier
        )

        self.bos_detector = BOSCHOCHDetector()

        self.fvg_detector = FVGDetector(
            atr_multiplier=fvg_atr_multiplier
        )

        self.ob_detector = OrderBlockDetector(
            displacement_multiplier=
            displacement_atr_multiplier
        )

        self.liquidity_detector = (
            LiquidityDetector(
                threshold=
                equal_level_threshold
            )
        )

        self.premium_discount = (
            PremiumDiscount()
        )

        self.bias_detector = (
            HigherTimeframeBias()
        )

    def generate_features(
        self,
        df_15m,
        df_higher_tf=None
    ):

        logger.info(
            "Starting market "
            "structure analysis..."
        )

        df = df_15m.copy()

        logger.info(
            "Detecting swings..."
        )

        swings = (
            self.swing_detector
            .detect_swings(df)
        )

        logger.info(
            f"Detected "
            f"{len(swings)} swings"
        )

        logger.info(
            "Detecting BOS "
            "and CHOCH..."
        )

        bos_features = (
            self.bos_detector
            .detect(
                df,
                swings
            )
        )

        logger.info(
            "Detecting FVGs..."
        )

        fvg_features = (
            self.fvg_detector
            .detect(df)
        )

        logger.info(
            "Detecting order "
            "blocks..."
        )

        ob_features = (
            self.ob_detector
            .detect(
                df,
                bos_features
            )
        )

        logger.info(
            "Detecting "
            "liquidity..."
        )

        liquidity_features = (
            self.liquidity_detector
            .detect(
                df,
                swings
            )
        )

        logger.info(
            "Calculating "
            "premium/discount..."
        )

        pd_features = (
            self.premium_discount
            .calculate(
                df,
                swings
            )
        )

        if df_higher_tf is not None:

            logger.info(
                "Calculating "
                "higher timeframe "
                "bias..."
            )

            bias_features = (
                self.bias_detector
                .calculate(
                    df_higher_tf
                )
            )

            df = df.merge(
                bias_features,
                on="timestamp",
                how="left"
            )

        df = df.merge(
            bos_features,
            on="timestamp",
            how="left"
        )

        df = df.merge(
            fvg_features,
            on="timestamp",
            how="left"
        )

        df = df.merge(
            ob_features,
            on="timestamp",
            how="left"
        )

        df = df.merge(
            liquidity_features,
            on="timestamp",
            how="left"
        )

        df = df.merge(
            pd_features,
            on="timestamp",
            how="left"
        )

        logger.info(
            "Market structure "
            "analysis completed."
        )

        return df