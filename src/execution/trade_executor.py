from datetime import datetime

from src.utils.logger import logger


class TradeExecutor:

    def __init__(
        self,
        exchange,
        risk_manager,
        paper_trading=True
    ):

        self.exchange = exchange
        self.risk_manager = risk_manager
        self.paper_trading = (
            paper_trading
        )

    def execute_trade(
        self,
        symbol,
        signal
    ):

        if signal["signal"] == "NONE":

            logger.info(
                f"No signal for "
                f"{symbol}"
            )

            return None

        if not (
            self.risk_manager
            .can_trade()
        ):

            logger.warning(
                "Risk manager "
                "blocked trade."
            )

            return None

        quantity = (
            self.risk_manager
            .calculate_position_size(
                signal["entry"],
                signal["stop_loss"]
            )
        )

        if quantity <= 0:

            logger.warning(
                "Invalid position "
                "size."
            )

            return None

        order = {

            "timestamp":
            datetime.utcnow(),

            "symbol":
            symbol,

            "side":
            signal["signal"],

            "entry":
            signal["entry"],

            "stop_loss":
            signal["stop_loss"],

            "take_profit":
            signal["take_profit"],

            "quantity":
            quantity,

            "probability":
            signal["probability"]
        }

        if self.paper_trading:

            logger.info(
                f"PAPER TRADE "
                f"EXECUTED: "
                f"{order}"
            )

            return order

        try:

            if (
                signal["signal"]
                ==
                "LONG"
            ):

                response = (
                    self.exchange
                    .place_order(
                        symbol=symbol,
                        side="buy",
                        quantity=quantity
                    )
                )

            else:

                response = (
                    self.exchange
                    .place_order(
                        symbol=symbol,
                        side="sell",
                        quantity=quantity
                    )
                )

            logger.info(
                f"LIVE ORDER "
                f"PLACED: "
                f"{response}"
            )

            return response

        except Exception as e:

            logger.error(
                f"Order execution "
                f"failed: {e}"
            )

            return None

    def close_trade(
        self,
        symbol,
        side,
        quantity,
        pnl
    ):

        self.risk_manager.register_trade_result(
            pnl
        )

        logger.info(
            f"Trade closed "
            f"{symbol} "
            f"{side} "
            f"PnL={pnl}"
        )

    def get_open_positions(self):

        try:

            positions = (
                self.exchange
                .get_positions()
            )

            return positions

        except Exception as e:

            logger.error(
                f"Failed to fetch "
                f"positions: {e}"
            )

            return []

    def cancel_order(
        self,
        order_id
    ):

        try:

            response = (
                self.exchange
                .cancel_order(
                    order_id
                )
            )

            logger.info(
                f"Cancelled order "
                f"{order_id}"
            )

            return response

        except Exception as e:

            logger.error(
                f"Failed cancelling "
                f"order: {e}"
            )

            return None