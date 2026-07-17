import pandas as pd
from ta.volatility import AverageTrueRange

from src.database.database_manager import DatabaseManager
from src.smc.market_structure_engine import MarketStructureEngine
from src.strategy.signal_generator import SignalGenerator
from src.backtest.trade_simulator import TradeSimulator

from src.utils.logger import logger


def add_atr(
    df: pd.DataFrame,
    window: int = 14
) -> pd.DataFrame:

    df = df.copy()

    atr = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=window
    )

    df["atr_14"] = atr.average_true_range()

    return df


def count_flags(
    df: pd.DataFrame
) -> dict:

    excluded = {
        "timestamp",
        "bos_count",
        "trend",
        "latest_swing_high",
        "latest_swing_low",
        "equal_high_count",
        "equal_low_count",
        "sweep_count"
    }

    counts = {}

    for col in df.columns:

        if col in excluded:
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

    return counts


class BacktestEngine:

    def __init__(
        self,
        risk_reward: float = 2.0
    ):

        self.db_manager = DatabaseManager()

        self.structure_engine = (
            MarketStructureEngine()
        )

        self.signal_generator = (
            SignalGenerator(
                risk_reward=risk_reward
            )
        )

        self.trade_simulator = (
            TradeSimulator(
                risk_reward=risk_reward
            )
        )

    def load_timeframe(
        self,
        symbol: str,
        timeframe: str
    ) -> pd.DataFrame:

        df = self.db_manager.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe
        )

        df = df.drop(
            columns=[
                "symbol",
                "timeframe"
            ],
            errors="ignore"
        )

        df = add_atr(df)

        df = (
            df
            .dropna(
                subset=["atr_14"]
            )
            .reset_index(drop=True)
        )

        return df

    def run(
        self,
        symbol: str
    ) -> dict:

        logger.info(
            f"===== Backtesting "
            f"{symbol} ====="
        )

        df_1h = self.load_timeframe(
            symbol,
            "1h"
        )

        df_30m = self.load_timeframe(
            symbol,
            "30m"
        )

        df_15m = self.load_timeframe(
            symbol,
            "15m"
        )

        df_5m = self.load_timeframe(
            symbol,
            "5m"
        )

        feat_1h = (
            self.structure_engine
            .generate_features(df_1h)
        )

        feat_30m = (
            self.structure_engine
            .generate_features(df_30m)
        )

        feat_15m = (
            self.structure_engine
            .generate_features(df_15m)
        )

        feat_5m = (
            self.structure_engine
            .generate_features(df_5m)
        )

        counts_1h = count_flags(
            feat_1h
        )

        counts_30m = count_flags(
            feat_30m
        )

        counts_15m = count_flags(
            feat_15m
        )

        counts_5m = count_flags(
            feat_5m
        )

        signals = (
            self.signal_generator
            .generate_signals(
                df_1h=feat_1h,
                df_30m=feat_30m,
                df_15m=feat_15m,
                df_5m=feat_5m
            )
        )

        logger.info(
            f"Generated "
            f"{len(signals)} signals"
        )

        trades = (
            self.trade_simulator
            .simulate_trades(
                signals=signals,
                df_5m=feat_5m
            )
        )

        logger.info(
            f"Simulated "
            f"{len(trades)} trades"
        )

        return self._build_stats(
            symbol=symbol,
            counts_1h=counts_1h,
            counts_30m=counts_30m,
            counts_15m=counts_15m,
            counts_5m=counts_5m,
            trades=trades,
            total_signals=len(signals)
        )

    def _build_stats(
        self,
        symbol,
        counts_1h,
        counts_30m,
        counts_15m,
        counts_5m,
        trades,
        total_signals
    ):

        if trades.empty:

            return {
                "symbol": symbol,
                "structure_counts": {
                    "1h": counts_1h,
                    "30m": counts_30m,
                    "15m": counts_15m,
                    "5m": counts_5m
                },
                "total_signals": total_signals,
                "long_signals": 0,
                "short_signals": 0,
                "wins": 0,
                "losses": 0,
                "open": 0,
                "win_rate": None,
                "total_r": 0,
                "profit_factor": None
            }

        wins = int(
            (
                trades["outcome"]
                == "WIN"
            ).sum()
        )

        losses = int(
            (
                trades["outcome"]
                == "LOSS"
            ).sum()
        )

        open_trades = int(
            (
                trades["outcome"]
                == "OPEN"
            ).sum()
        )

        closed = wins + losses

        win_rate = (
            wins / closed
            if closed > 0
            else None
        )

        total_r = (
            trades["pnl_r"]
            .dropna()
            .sum()
        )

        gross_win_r = (
            trades.loc[
                trades["outcome"] == "WIN",
                "pnl_r"
            ].sum()
        )

        gross_loss_r = abs(
            trades.loc[
                trades["outcome"] == "LOSS",
                "pnl_r"
            ].sum()
        )

        profit_factor = (
            gross_win_r /
            gross_loss_r
            if gross_loss_r > 0
            else None
        )

        return {
            "symbol": symbol,

            "structure_counts": {
                "1h": counts_1h,
                "30m": counts_30m,
                "15m": counts_15m,
                "5m": counts_5m
            },

            "total_signals":
            total_signals,

            "long_signals":
            int(
                (
                    trades["direction"]
                    == "LONG"
                ).sum()
            ),

            "short_signals":
            int(
                (
                    trades["direction"]
                    == "SHORT"
                ).sum()
            ),

            "wins":
            wins,

            "losses":
            losses,

            "open":
            open_trades,

            "win_rate":
            win_rate,

            "total_r":
            total_r,

            "profit_factor":
            profit_factor,

            "trades":
            trades
        }

    def close(self):

        self.db_manager.close()