import pandas as pd

from src.utils.logger import logger


class TradeSimulator:

    def __init__(
        self,
        risk_reward: float = 2.0
    ):
        self.risk_reward = risk_reward

    def simulate_trades(
        self,
        signals: pd.DataFrame,
        df_5m: pd.DataFrame
    ) -> pd.DataFrame:

        if signals.empty:

            logger.info(
                "No signals to simulate."
            )

            return pd.DataFrame()

        df_5m = (
            df_5m
            .sort_values(
                "timestamp"
            )
            .reset_index(
                drop=True
            )
        )

        timestamp_index = {
            ts: i
            for i, ts in enumerate(
                df_5m["timestamp"]
            )
        }

        trades = []

        for _, signal in signals.iterrows():

            entry_timestamp = (
                signal["timestamp"]
            )

            direction = (
                signal["direction"]
            )

            entry = signal["entry"]

            stop_loss = (
                signal["stop_loss"]
            )

            take_profit = (
                signal["take_profit"]
            )

            start_idx = (
                timestamp_index.get(
                    entry_timestamp
                )
            )

            if start_idx is None:
                continue

            outcome = "OPEN"

            exit_price = None
            exit_timestamp = None

            for i in range(
                start_idx + 1,
                len(df_5m)
            ):

                candle = (
                    df_5m.iloc[i]
                )

                if direction == "LONG":

                    sl_hit = (
                        candle["low"]
                        <= stop_loss
                    )

                    tp_hit = (
                        candle["high"]
                        >= take_profit
                    )

                    # conservative assumption
                    if sl_hit and tp_hit:

                        outcome = "LOSS"

                        exit_price = (
                            stop_loss
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

                    elif sl_hit:

                        outcome = "LOSS"

                        exit_price = (
                            stop_loss
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

                    elif tp_hit:

                        outcome = "WIN"

                        exit_price = (
                            take_profit
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

                else:

                    sl_hit = (
                        candle["high"]
                        >= stop_loss
                    )

                    tp_hit = (
                        candle["low"]
                        <= take_profit
                    )

                    if sl_hit and tp_hit:

                        outcome = "LOSS"

                        exit_price = (
                            stop_loss
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

                    elif sl_hit:

                        outcome = "LOSS"

                        exit_price = (
                            stop_loss
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

                    elif tp_hit:

                        outcome = "WIN"

                        exit_price = (
                            take_profit
                        )

                        exit_timestamp = (
                            candle[
                                "timestamp"
                            ]
                        )

                        break

            pnl_r = None

            if outcome == "WIN":
                pnl_r = (
                    self.risk_reward
                )

            elif outcome == "LOSS":
                pnl_r = -1.0

            trades.append(
                {
                    "timestamp":
                    entry_timestamp,

                    "direction":
                    direction,

                    "entry":
                    entry,

                    "stop_loss":
                    stop_loss,

                    "take_profit":
                    take_profit,

                    "outcome":
                    outcome,

                    "exit_price":
                    exit_price,

                    "exit_timestamp":
                    exit_timestamp,

                    "pnl_r":
                    pnl_r
                }
            )

        logger.info(
            f"Simulated "
            f"{len(trades)} trades."
        )

        return pd.DataFrame(
            trades
        )