import logging
import os

logger = logging.getLogger("algo_system")

# Change this one line to switch modes:
# logging.INFO   -> clean, counts/summaries only (normal runs)
# logging.DEBUG  -> full per-candle trace (debugging sessions)
LOG_LEVEL = logging.INFO

logger.setLevel(LOG_LEVEL)

if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    os.makedirs("logs", exist_ok=True)

    file_handler = logging.FileHandler(
        "logs/backtest_debug.log",
        mode="w",
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)