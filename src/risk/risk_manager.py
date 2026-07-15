from config import (
    RISK_PER_TRADE,
    DAILY_LOSS_LIMIT,
    MAX_DRAWDOWN
)

from src.utils.logger import logger


class RiskManager:

    def __init__(
        self,
        account_balance,
        risk_per_trade=RISK_PER_TRADE,
        daily_loss_limit=DAILY_LOSS_LIMIT,
        max_drawdown=MAX_DRAWDOWN
    ):

        self.account_balance = (
            account_balance
        )

        self.initial_balance = (
            account_balance
        )

        self.risk_per_trade = (
            risk_per_trade
        )

        self.daily_loss_limit = (
            daily_loss_limit
        )

        self.max_drawdown = (
            max_drawdown
        )

        self.daily_loss = 0

    def calculate_position_size(
        self,
        entry_price,
        stop_loss
    ):

        risk_amount = (
            self.account_balance
            *
            self.risk_per_trade
        )

        stop_distance = abs(
            entry_price
            -
            stop_loss
        )

        if stop_distance == 0:

            logger.warning(
                "Stop distance is zero."
            )

            return 0

        quantity = (
            risk_amount
            /
            stop_distance
        )

        logger.info(
            f"Position Size="
            f"{quantity:.6f}"
        )

        return quantity

    def can_trade(self):

        daily_loss_pct = (
            self.daily_loss
            /
            self.initial_balance
        )

        current_drawdown = (
            (
                self.initial_balance
                -
                self.account_balance
            )
            /
            self.initial_balance
        )

        if (
            daily_loss_pct
            >=
            self.daily_loss_limit
        ):

            logger.warning(
                "Daily loss limit hit."
            )

            return False

        if (
            current_drawdown
            >=
            self.max_drawdown
        ):

            logger.warning(
                "Maximum drawdown hit."
            )

            return False

        return True

    def register_trade_result(
        self,
        pnl
    ):

        self.account_balance += pnl

        if pnl < 0:
            self.daily_loss += abs(
                pnl
            )

        logger.info(
            f"PnL={pnl:.2f} "
            f"Balance="
            f"{self.account_balance:.2f}"
        )

    def reset_daily_loss(self):

        self.daily_loss = 0

        logger.info(
            "Daily loss reset."
        )

    def get_risk_report(self):

        drawdown = (
            (
                self.initial_balance
                -
                self.account_balance
            )
            /
            self.initial_balance
        )

        report = {

            "balance":
            self.account_balance,

            "daily_loss":
            self.daily_loss,

            "drawdown":
            drawdown,

            "risk_per_trade":
            self.risk_per_trade,

            "daily_loss_limit":
            self.daily_loss_limit,

            "max_drawdown":
            self.max_drawdown
        }

        return report