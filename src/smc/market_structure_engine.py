import pandas as pd

from src.smc.swing_detector import SwingDetector
from src.smc.bos_choch_detector import BOSCHOCHDetector
from src.smc.fvg_detector import FVGDetector
from src.smc.order_block_detector import OrderBlockDetector
from src.smc.liquidity_detector import LiquidityDetector
from src.smc.premium_discount import PremiumDiscountDetector
from src.smc.higher_tf_bias import HigherTFBias

from src.utils.logger import logger


def log_feature_counts(
    label: str,
    df: pd.DataFrame
) -> None:
    """
    Automatically counts binary structure columns such as:

    bullish_fvg_present
    bearish_fvg_present
    bullish_ob_present
    bearish_ob_present
    bullish_bos
    bearish_bos
    bullish_choch
    bearish_choch
    bullish_sweep
    bearish_sweep

    Supports:
    - 0 / 1
    - True / False
    - NaN mixed with binary values
    """

    counts = {}

    logger.info(
        f"{label} available columns: "
        f"{df.columns.tolist()}"
    )

    ignore_columns = [
        "timestamp",
        "bos_count",
        "trend",
        "latest_swing_high",
        "latest_swing_low"
    ]

    for col in df.columns:

        if col in ignore_columns:
            continue

        series = (
            df[col]
            .fillna(0)
        )

        is_binary = (
            series.dtype == bool
            or
            series.isin(
                [0, 1, True, False]
            ).all()
        )

        if is_binary:

            total = int(
                series.astype(int).sum()
            )

            if total > 0:
                counts[col] = total

    if counts:

        summary = " | ".join(
            f"{k}: {v}"
            for k, v in counts.items()
        )

        logger.info(
            f"{label} counts -> "
            f"{summary}"
        )

    else:

        logger.info(
            f"{label} counts -> "
            f"none detected"
        )


class MarketStructureEngine:
    """
    Orchestrates all SMC detectors (swings, BOS/CHOCH, FVG, order blocks,
    liquidity, premium/discount, and optional higher timeframe bias)
    and merges their output into a single feature dataframe.
    """

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
            displacement_multiplier=displacement_atr_multiplier
        )

        self.liquidity_detector = LiquidityDetector(
            threshold_pct=equal_level_threshold
        )

        self.premium_discount_detector = PremiumDiscountDetector()

        self.higher_tf_bias = HigherTFBias()

    def generate_features(
        self,
        df_15m: pd.DataFrame,
        df_higher_tf: pd.DataFrame = None
    ) -> pd.DataFrame:

        logger.info("Starting market structure analysis...")

        df = df_15m.copy()

        # ======================================
        # Swings
        # ======================================
        logger.info("Detecting swings...")

        swings = self.swing_detector.detect_swings(df)
        logger.info(f"df timestamp dtype: {df['timestamp'].dtype}, sample: {df['timestamp'].iloc[0]!r}")
        if not swings.empty:
            logger.info(f"swings timestamp dtype: {swings['timestamp'].dtype}, sample: {swings['timestamp'].iloc[0]!r}")

        logger.info(f"Detected {len(swings)} swings")

        # ======================================
        # BOS + CHOCH
        # ======================================
        logger.info("Detecting BOS and CHOCH...")

        bos_features = self.bos_detector.detect(df, swings)

        log_feature_counts("BOS/CHOCH", bos_features)

        # ======================================
        # FVG
        # ======================================
        logger.info("Detecting FVGs...")

        fvg_features = self.fvg_detector.detect(df)

        log_feature_counts("FVG", fvg_features)
        logger.info(
            f"FVG columns: "
            f"{list(fvg_features.columns)}"
        )

        # ======================================
        # Order Blocks
        # ======================================
        logger.info("Detecting Order Blocks...")

        ob_features = self.ob_detector.detect(df, bos_features)

        log_feature_counts("Order Blocks", ob_features)
        logger.info(
            f"OB columns: "
            f"{list(ob_features.columns)}"
        )

        # ======================================
        # Liquidity
        # ======================================
        logger.info("Detecting liquidity...")

        liquidity_features = self.liquidity_detector.detect(df, swings)

        log_feature_counts("Liquidity/Sweeps", liquidity_features)

        # ======================================
        # Premium / Discount
        # ======================================
        logger.info("Calculating premium/discount...")

        pd_features = self.premium_discount_detector.detect(df, swings)

        # ======================================
        # Higher Timeframe Bias
        # ======================================
        if df_higher_tf is not None:

            logger.info("Calculating higher timeframe bias...")

            bias_features = self.higher_tf_bias.calculate(df_higher_tf)

            df = df.merge(bias_features, on="timestamp", how="left")

            df["bias"] = df["bias"].ffill()
            df["bias_value"] = df["bias_value"].ffill()

        # ======================================
        # Merge Features
        # ======================================
        df = df.merge(bos_features, on="timestamp", how="left")
        df = df.merge(fvg_features, on="timestamp", how="left")
        df = df.merge(ob_features, on="timestamp", how="left")
        df = df.merge(liquidity_features, on="timestamp", how="left")
        df = df.merge(pd_features, on="timestamp", how="left")
        logger.info(
        f"Final columns: "
        f"{list(df.columns)}"
    )

        logger.info("Market structure analysis completed.")

        return df