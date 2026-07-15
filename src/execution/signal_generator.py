import pandas as pd
import joblib

from src.ml.utils import MLUtils
from src.utils.logger import logger


class SignalGenerator:

    def __init__(
        self,
        long_model_path,
        short_model_path,
        long_threshold=0.65,
        short_threshold=0.65
    ):

        self.long_model = (
            MLUtils.load_model(
                long_model_path
            )
        )

        self.short_model = (
            MLUtils.load_model(
                short_model_path
            )
        )

        self.long_threshold = (
            long_threshold
        )

        self.short_threshold = (
            short_threshold
        )

    def calculate_levels(
        self,
        row,
        side
    ):

        entry = row["close"]

        atr = row["atr_14"]

        risk = atr * 1.5

        if side == "LONG":

            sl = entry - risk
            tp = entry + (risk * 2)

        else:

            sl = entry + risk
            tp = entry - (risk * 2)

        return (
            entry,
            sl,
            tp
        )

    def smc_filter_long(
        self,
        row
    ):

        conditions = [

            row.get(
                "bullish_bos",
                0
            ) == 1,

            row.get(
                "discount_zone",
                0
            ) == 1,

            row.get(
                "bullish_ob_distance",
                999
            ) < 0.02,

            row.get(
                "bias_value",
                0
            ) >= 0
        ]

        return all(
            conditions
        )

    def smc_filter_short(
        self,
        row
    ):

        conditions = [

            row.get(
                "bearish_bos",
                0
            ) == 1,

            row.get(
                "premium_zone",
                0
            ) == 1,

            row.get(
                "bearish_ob_distance",
                999
            ) < 0.02,

            row.get(
                "bias_value",
                0
            ) <= 0
        ]

        return all(
            conditions
        )

    def build_feature_vector(
        self,
        row
    ):

        excluded = [

            "timestamp",
            "symbol",

            "long_label",
            "short_label",

            "entry_price",
            "long_sl",
            "long_tp",
            "short_sl",
            "short_tp"
        ]

        features = (
            row
            .drop(
                labels=excluded,
                errors="ignore"
            )
            .to_frame()
            .T
        )

        return features

    def generate_signal(
        self,
        row
    ):

        signal = {
            "signal": "NONE",
            "probability": 0,
            "entry": None,
            "stop_loss": None,
            "take_profit": None
        }

        X = self.build_feature_vector(
            row
        )

        # =====================
        # LONG SETUP
        # =====================

        if self.smc_filter_long(
            row
        ):

            probability = (
                self.long_model
                .predict_proba(X)[0][1]
            )

            if (
                probability
                >=
                self.long_threshold
            ):

                (
                    entry,
                    sl,
                    tp
                ) = (
                    self.calculate_levels(
                        row,
                        "LONG"
                    )
                )

                signal = {

                    "signal":
                    "LONG",

                    "probability":
                    probability,

                    "entry":
                    entry,

                    "stop_loss":
                    sl,

                    "take_profit":
                    tp
                }

                logger.info(
                    f"LONG signal "
                    f"generated "
                    f"prob={probability:.2f}"
                )

                return signal

        # =====================
        # SHORT SETUP
        # =====================

        if self.smc_filter_short(
            row
        ):

            probability = (
                self.short_model
                .predict_proba(X)[0][1]
            )

            if (
                probability
                >=
                self.short_threshold
            ):

                (
                    entry,
                    sl,
                    tp
                ) = (
                    self.calculate_levels(
                        row,
                        "SHORT"
                    )
                )

                signal = {

                    "signal":
                    "SHORT",

                    "probability":
                    probability,

                    "entry":
                    entry,

                    "stop_loss":
                    sl,

                    "take_profit":
                    tp
                }

                logger.info(
                    f"SHORT signal "
                    f"generated "
                    f"prob={probability:.2f}"
                )

                return signal

        logger.info(
            "No valid signal found."
        )

        return signal