from config import SYMBOLS
from src.backtest.backtest_engine import BacktestEngine
from src.utils.logger import logger


def print_report(stats: dict):

    print(f"\n{'=' * 60}")
    print(f"BACKTEST REPORT — {stats['symbol']}")
    print(f"{'=' * 60}")

    for tf, counts in stats["structure_counts"].items():

        print(f"\n[{tf}] Structure counts:")

        if not counts:
            print("  none detected")
            continue

        for key, value in counts.items():
            print(f"  {key}: {value}")

    print(f"\nTotal signals: {stats['total_signals']}")

    if stats["total_signals"] == 0:
        print("No trades generated.")
        return

    print(f"  LONG:  {stats.get('long_signals', 0)}")
    print(f"  SHORT: {stats.get('short_signals', 0)}")

    print(f"\nWins:   {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Open:   {stats['open']}")

    if stats["win_rate"] is not None:
        print(f"Win rate: {stats['win_rate'] * 100:.2f}%")

    print(f"Total R: {stats['total_r']:.2f}")

    if stats["profit_factor"] is not None:
        print(f"Profit factor: {stats['profit_factor']:.2f}")


def main():

    engine = BacktestEngine(risk_reward=2.0)

    all_stats = []

    for symbol in SYMBOLS:

        try:
            stats = engine.run(symbol)
            all_stats.append(stats)
            print_report(stats)

        except Exception as e:
            logger.error(f"Backtest failed for {symbol}: {e}")

    engine.close()

    print(f"\n{'=' * 60}")
    print("SUMMARY — ALL SYMBOLS")
    print(f"{'=' * 60}")

    total_wins = sum(
    s.get("wins", 0)
    for s in all_stats
    )

    total_losses = sum(
        s.get("losses", 0)
        for s in all_stats
    )

    total_r = sum(
        s.get("total_r", 0)
        for s in all_stats
    )

    closed = total_wins + total_losses

    if closed > 0:
        print(f"Overall win rate: {(total_wins / closed) * 100:.2f}%")

    print(f"Overall total R: {total_r:.2f}")


if __name__ == "__main__":
    main()