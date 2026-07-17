import pandas as pd

from src.utils.logger import logger


class SignalGenerator:

    def __init__(
        self,
        risk_reward: float = 2.0
    ):
        self.risk_reward = risk_reward

    def _align(
        self,
        base: pd.DataFrame,
        higher: pd.DataFrame
    ) -> pd.DataFrame:

        base_sorted = (
            base
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        higher_sorted = (
            higher
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        return pd.merge_asof(
            base_sorted,
            higher_sorted,
            on="timestamp",
            direction="backward"
        )

    def generate_signals(
        self,
        df_1h: pd.DataFrame,
        df_30m: pd.DataFrame,
        df_15m: pd.DataFrame,
        df_5m: pd.DataFrame
    ) -> pd.DataFrame:

        # =========================================
        # 1H trend -> 30m
        # =========================================

        htf_bias = (
            df_1h[
                [
                    "timestamp",
                    "trend"
                ]
            ]
            .rename(
                columns={
                    "trend":
                    "htf_trend"
                }
            )
        )

        merged_30m = self._align(
            df_30m,
            htf_bias
        )
        logger.info(
            f"30m columns after alignment: "
            f"{list(merged_30m.columns)}"
        )

        # =========================================
        # 30m POI -> 15m
        # =========================================

        poi_cols = [
            "timestamp",
            "htf_trend",

            "bullish_ob_present",
            "bearish_ob_present",

            "bullish_fvg_present",
            "bearish_fvg_present"
        ]

        merged_15m = self._align(
            df_15m.drop(
                columns=[
                    "bullish_ob_present",
                    "bearish_ob_present",
                    "bullish_fvg_present",
                    "bearish_fvg_present"
                ],
                errors="ignore"
            ),
            merged_30m[poi_cols]
        )
        logger.info(
            f"15m columns after alignment: "
            f"{list(merged_15m.columns)}"
        )
        # =========================================
        # 15m confirmation -> 5m
        # =========================================

        conf_cols = [
            "timestamp",
            "htf_trend",

            "bullish_ob_present",
            "bearish_ob_present",

            "bullish_fvg_present",
            "bearish_fvg_present",

            "bullish_sweep",
            "bearish_sweep",

            "bullish_bos",
            "bearish_bos"
        ]

        renamed_15m = (
            merged_15m[
                conf_cols
            ]
            .rename(
                columns={
                    "bullish_sweep":
                    "sweep_bullish_15m",

                    "bearish_sweep":
                    "sweep_bearish_15m",

                    "bullish_bos":
                    "bos_bullish_15m",

                    "bearish_bos":
                    "bos_bearish_15m"
                }
            )
        )

        merged_5m = self._align(
            df_5m.drop(
                columns=[
                    "bullish_ob_present",
                    "bearish_ob_present",
                    "bullish_fvg_present",
                    "bearish_fvg_present"
                ],
                errors="ignore"
            ),
            renamed_15m
        )
        logger.info(f"merged_5m sample row: {merged_5m[['bullish_ob_present','bearish_ob_present','bullish_fvg_present','bearish_fvg_present']].sum().to_dict()}")

        # =========================================
        # Replace NaNs in binary columns
        # =========================================

        binary_cols = [
            "bullish_ob_present",
            "bearish_ob_present",

            "bullish_fvg_present",
            "bearish_fvg_present",

            "sweep_bullish_15m",
            "sweep_bearish_15m",

            "bos_bullish_15m",
            "bos_bearish_15m",

            "bullish_choch",
            "bearish_choch"
        ]

        for col in binary_cols:

            if col in merged_5m.columns:

                merged_5m[col] = (
                    merged_5m[col]
                    .fillna(0)
                    .astype(int)
                )

        logger.info(
            f"Signal generator columns: "
            f"{merged_5m.columns.tolist()}"
        )

        signals = []

        for _, row in merged_5m.iterrows():

            timestamp = row["timestamp"]

            close_price = row["close"]

            htf_trend = row.get(
                "htf_trend"
            )

            # =====================================
            # LONG CONDITIONS
            # =====================================

            long_conditions = (
            htf_trend == 1
            and
            (
                row.get("bullish_ob_present", 0) == 1
                or
                row.get("bullish_fvg_present", 0) == 1
            )
            and
            (
                row.get("sweep_bearish_15m", 0) == 1
                or
                row.get("bos_bullish_15m", 0) == 1
            )
            and
            row.get("bullish_choch", 0) == 1
        )

            if htf_trend == 1:

                logger.debug(
                    f"LONG CHECK | "
                    f"OB={row.get('bullish_ob_present')} | "
                    f"FVG={row.get('bullish_fvg_present')} | "
                    f"SWEEP={row.get('sweep_bearish_15m')} | "
                    f"BOS={row.get('bos_bullish_15m')} | "
                    f"CHOCH={row.get('bullish_choch')} | "
                    f"SL={row.get('latest_swing_low')}"
                )

            if long_conditions:

                stop_loss = row.get(
                    "latest_swing_low"
                )

                if (
                    stop_loss is None
                    or
                    pd.isna(stop_loss)
                ):

                    stop_loss = (
                        close_price * 0.99
                    )

                if stop_loss < close_price:

                    risk = (
                        close_price
                        -
                        stop_loss
                    )

                    take_profit = (
                        close_price
                        +
                        (
                            risk
                            *
                            self.risk_reward
                        )
                    )

                    signals.append(
                        {
                            "timestamp":
                            timestamp,

                            "direction":
                            "LONG",

                            "entry":
                            close_price,

                            "stop_loss":
                            stop_loss,

                            "take_profit":
                            take_profit,

                            "risk":
                            risk,

                            "reward":
                            (
                                risk
                                *
                                self.risk_reward
                            )
                        }
                    )

                    logger.info(
                        f"LONG signal "
                        f"@ {timestamp} "
                        f"entry={close_price} "
                        f"sl={stop_loss} "
                        f"tp={take_profit}"
                    )

            # =====================================
            # SHORT CONDITIONS
            # =====================================

            short_conditions = (
            htf_trend == -1
            and
            (
                row.get("bearish_ob_present", 0) == 1
                or
                row.get("bearish_fvg_present", 0) == 1
            )
            and
            (
                row.get("sweep_bullish_15m", 0) == 1
                or
                row.get("bos_bearish_15m", 0) == 1
            )
            and
            row.get("bearish_choch", 0) == 1
        )

            if htf_trend == -1:

                logger.debug(
                    f"SHORT CHECK | "
                    f"OB={row.get('bearish_ob_present')} | "
                    f"FVG={row.get('bearish_fvg_present')} | "
                    f"SWEEP={row.get('sweep_bullish_15m')} | "
                    f"BOS={row.get('bos_bearish_15m')} | "
                    f"CHOCH={row.get('bearish_choch')} | "
                    f"SL={row.get('latest_swing_high')}"
                )

            if short_conditions:

                stop_loss = row.get(
                    "latest_swing_high"
                )

                if (
                    stop_loss is None
                    or
                    pd.isna(stop_loss)
                ):

                    stop_loss = (
                        close_price * 1.01
                    )

                if stop_loss > close_price:

                    risk = (
                        stop_loss
                        -
                        close_price
                    )

                    take_profit = (
                        close_price
                        -
                        (
                            risk
                            *
                            self.risk_reward
                        )
                    )

                    signals.append(
                        {
                            "timestamp":
                            timestamp,

                            "direction":
                            "SHORT",

                            "entry":
                            close_price,

                            "stop_loss":
                            stop_loss,

                            "take_profit":
                            take_profit,

                            "risk":
                            risk,

                            "reward":
                            (
                                risk
                                *
                                self.risk_reward
                            )
                        }
                    )

                    logger.info(
                        f"SHORT signal "
                        f"@ {timestamp} "
                        f"entry={close_price} "
                        f"sl={stop_loss} "
                        f"tp={take_profit}"
                    )

        logger.info(
            f"Signal generation completed. "
            f"{len(signals)} signals found."
        )

        return pd.DataFrame(
            signals
        )